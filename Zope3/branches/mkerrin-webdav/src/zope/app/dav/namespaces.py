##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""WebDAV namespace management utilities

$Id$
"""
__docformat__ = 'restructuredtext'

from persistent import Persistent
from BTrees.OOBTree import OOBTree
from zope.interface import implements
from zope import component
from zope.schema import getFieldNames
from zope.schema import Field
from zope.app.container.contained import Contained

from interfaces import IDAVWidget
from interfaces import INamespaceManager, ILiveNamespaceManager, \
     INamespaceRegistry
from interfaces import IDAVOpaqueNamespaces
from common import DAVConflictError
from widget import DAVOpaqueWidget


class NamespaceManager(object):
    implements(ILiveNamespaceManager)

    def __init__(self, namespace, schemas = [], restricted_properties = [],
                 interfaceType = None):
        self.namespace = namespace
        # property name -> schema lookup, schema values should be the
        # smallest possible schema containing the property.
        self.properties = {}
        # a list of property names which should not be listed and rendered
        # in response to a allprop PROPFIND request.
        self.restricted_properties = restricted_properties
        # property name -> widget class to use when rendering a property.
        self.widgets = {}
        # optional interface to use with the APIDOC - all schemas will be
        # declared to implement this interface type. Hence they will show
        # up in the interface types section of the APIDOC tool.
        self.interfaceType = interfaceType

        for schema in schemas:
            self.registerSchema(schema)

    def registerSchema(self, schema, restricted_properties = []):
        props = {}
        for baseschema in (schema,) + schema.getBases():
            for fieldname in getFieldNames(baseschema):
                if props.has_key(fieldname):
                    oldschema = props[fieldname]
                    if oldschema.isOrExtends(baseschema):
                        pass
                    elif baseschema.isOrExtends(oldschema):
                        props[fieldname] = baseschema
                    else:
                        raise TypeError, "duplicate property in %s" % schema
                props[fieldname] = baseschema

        for propname in props:
            if self.properties.has_key(propname):
                oldschema = self.properties[propname]
                newschema = props[propname]
                if oldschema.isOrExtends(newschema):
                    pass
                elif newschema.isOrExtends(oldschema):
                    self.properties[propname] = newschema
                else:
                    raise TypeError, "duplicate property %s %s %s" %(
                        propname, schema, oldschema)
            else:
                self.properties[propname] = props[propname]

        for propname in restricted_properties:
            if propname not in self.restricted_properties:
                self.restricted_properties.append(propname)

    def registerWidget(self, propname, widget):
        if not self.properties.has_key(propname):
            raise TypeError, \
                "There must exist a property for the widget you are registering"
        self.widgets[propname] = widget

    def _getStorageAdapter(self, object, name, default = None):
        schema = self.properties.get(name, None)
        if schema is not None:
            return component.queryAdapter(object, schema, default = default)

        return default

    def isLiveNamespace(self):
        return True

    def queryProperty(self, object, name, default = None):
        adapter = self._getStorageAdapter(object, name, None)
        if adapter is None:
            return default

        return self.getProperty(object, name)

    def getProperty(self, object, name):
        adapter = self._getStorageAdapter(object, name)
        if adapter is None:
            raise TypeError, \
                  "Property %s doesn't exist for the context object" % name

        field = self.properties[name][name]
        field = field.bind(adapter)

        return field

    def removeProperty(self, object, name):
        # XXX should this level of support for the WebDAV protocol be supported
        # in this utility.
        adapter = self._getStorageAdapter(object, name)
        if adapter is None:
            return # nothing to do :-)
        prop = self.getProperty(object, name)

        if prop.readonly:
            raise DAVConflictError(name, "property is readonly")

        if prop.required:
            if prop.default is None:
                # Clearing a required property is a conflict
                raise DAVConflictError(name, "the property is required")
            # Reset the field to the default if a value is required
            prop.set(adapter, prop.default)
        else:
            prop.set(adapter, prop.missing_value)

    def getWidget(self, object, request, name, ns_prefix):
        adapter = self._getStorageAdapter(object, name)
        if adapter is None:
            raise TypeError, \
                  "Failed to find the property %s for the current context" \
                  " object" % name

        field = self.properties[name][name]
        field = field.bind(adapter)

        value = field.get(adapter)

        if self.widgets.has_key(name):
            widget = self.widgets[name](field, request)
        else:
            widget = component.getMultiAdapter((field, request), IDAVWidget)

        widget.setRenderedValue(value)
        widget.setNamespace(self.namespace, ns_prefix)

        return widget

    def getAllPropertyNames(self, object, restricted = False):
        for propname, schema in self.properties.items():
            adapter = component.queryAdapter(object, schema, default = None)
            if adapter is not None and \
               (restricted is False or \
                propname not in self.restricted_properties):
                yield propname

    def getAllProperties(self, object, restricted = False):
        for propname, schema in self.properties.items():
            adapter = component.queryAdapter(object, schema, default = None)
            if adapter is not None:
                if restricted is False or \
                       propname not in self.restricted_properties:
                    field = schema[propname]
                    field = field.bind(adapter)
                    yield field

    def isRestrictedProperty(self, object, name):
        if self.queryProperty(object, name, None) is not None:
            if name in self.restricted_properties:
                return True
        return False

################################################################################
#
# Utility to handle all namespaces including dead property namespaces.
#
################################################################################

class DeadPropertyField(Field):
    """Dead properties are stored in dictionary-like objects. This are the
    storage adapters that implement the IDAVOpaqueNamespace interface.
    """

    def __init__(self, namespace, **kw):
        super(DeadPropertyField, self).__init__(**kw)
        self.namespace = namespace

    def get(self, object):
        return object.getProperty(self.namespace, self.__name__)

    def query(self, object, default = None):
        if object.hasProperty(self.namespace, self.__name__):
            return self.get(object)
        return default

    def set(self, object, value):
        object.setProperty(self.namespace, self.__name__, value)


class DeadNamespaceManager(Persistent, Contained):
    implements(INamespaceManager)

    def __init__(self, namespace):
        self.namespace = namespace

    def isLiveNamespace(self):
        return False

    def queryProperty(self, object, name, default = None):
        adapter = IDAVOpaqueNamespaces(object, None)
        if adapter is None:
            return default

        if adapter.hasProperty(self.namespace, name):
            return self.getProperty(object, name)

        return default

    def getProperty(self, object, name):
        adapter = IDAVOpaqueNamespaces(object)

        field = DeadPropertyField(namespace = self.namespace,
                                  title = u'Dead Property for %s' % name,
                                  __name__ = name, required = False,
                                  readonly = False, default = None)
        field = field.bind(adapter)

        return field

    def removeProperty(self, object, name):
        adapter = IDAVOpaqueNamespaces(object, None)
        if adapter is None or not adapter.hasProperty(self.namespace, name):
            return # nothing to do

        adapter.removeProperty(self.namespace, name)

    def getWidget(self, object, request, name, ns_prefix):
        adapter = IDAVOpaqueNamespaces(object)
        prop = self.getProperty(object, name)

        value = None
        if adapter.hasProperty(self.namespace, name):
            value = adapter.getProperty(self.namespace, name)

        widget = DAVOpaqueWidget(prop, request)
        widget.setRenderedValue(value)
        widget.setNamespace(self.namespace, ns_prefix)

        return widget

    def getAllPropertyNames(self, object, restricted = True):
        adapter = IDAVOpaqueNamespaces(object, None)
        if adapter is None:
            return []

        names = []
        for propname in adapter.get(self.namespace, {}):
            names.append(propname)

        return names

    def getAllProperties(self, object, restricted = True):
        for propname in self.getAllPropertyNames(object):
            yield DeadPropertyField(namespace = self.namespace,
                                    title = u'Dead Property for %s' % propname,
                                    __name__ = propname,
                                    required = False,
                                    readonly = False,
                                    default = None)

    def isRestrictedProperty(self, object, name):
        return False


class LocalNamespaceRegistry(Persistent, Contained):
    """Supports dead namespaces.
    """
    implements(INamespaceRegistry)

    def __init__(self):
        self.namespaces = OOBTree()

    def getNamespaceManager(self, namespace):
        nsmanager = self.namespaces.get(namespace, None)
        if nsmanager is not None:
            return nsmanager

        nsmanager = component.queryUtility(INamespaceManager, namespace,
                                           default = None)
        if nsmanager is not None:
            return nsmanager

        nsmanager = DeadNamespaceManager(namespace)
        self.namespaces[namespace] = nsmanager
        return nsmanager

    def queryNamespaceManager(self, namespace, default = None):
        nsmanager = self.namespaces.get(namespace, None)
        if nsmanager is not None:
            return nsmanager

        nsmanager = component.queryUtility(INamespaceManager, namespace,
                                           default = None)
        if nsmanager is not None:
            return nsmanager

        nsmanager = DeadNamespaceManager(namespace)
        self.namespaces[namespace] = nsmanager
        return nsmanager

    def hasNamespaceManager(self, namespace):
        nsmanager = self.queryNamespaceManager(namespace, None)
        if nsmanager is None:
            return False
        return True

    def getAllNamespaceManagers(self):
        for nsmanager in self.namespaces.values():
            yield nsmanager
        for ns, nsmanager in component.getUtilitiesFor(INamespaceManager):
            yield nsmanager


class NamespaceRegistry(object):
    implements(INamespaceRegistry)

    def getNamespaceManager(self, namespace):
        return component.getUtility(INamespaceManager, namespace)

    def queryNamespaceManager(self, namespace, default = None):
        return component.queryUtility(INamespaceManager, namespace,
                                      default = default)

    def hasNamespaceManager(self, namespace):
        return self.queryNamespaceManager(namespace, None) is not None

    def getAllNamespaceManagers(self):
        for namespace, nsmanager in \
                component.getUtilitiesFor(INamespaceManager):
            yield nsmanager

namespaceRegistry = NamespaceRegistry()
