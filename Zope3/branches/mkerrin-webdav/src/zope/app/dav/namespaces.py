from zope.interface import Interface, implements, Attribute
from zope import component
from zope.schema import getFieldNamesInOrder, getFieldNames

from interfaces import IDAVNamespaceType, IDAVWidget
from interfaces import INamespaceManager


class NamespaceManager(object):
    implements(INamespaceManager)

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
            if not self.restricted_properties.has_key(propname):
                self.restricted_properties.append(propname)

    def registerWidget(self, propname, widget):
        if not self.properties.has_key(propname):
            raise TypeError, \
                "There must exist a property for the widget you are registering"
        self.widgets[propname] = widget

    def _getAdapter(self, object, propname):
        schema = self.properties.get(propname, None)
        if schema is not None:
            return component.queryAdapter(object, schema, default = None)

        return None

    def hasProperty(self, object, propname):
        adapter = self._getAdapter(object, propname)
        if adapter is None:
            return False
        return True

    def getProperty(self, object, name):
        adapter = self._getAdapter(object, name)
        if adapter is None:
            raise TypeError, "no property found"

        field = self.properties[name][name]
        field = field.bind(adapter)

        return field

    def getWidget(self, object, request, name, ns_prefix):
        adapter = self._getAdapter(object, name)
        if adapter is None:
            raise TypeError, "no property found"

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
        if self.hasProperty(object, name):
            if name in self.restricted_properties:
                return True
        return False
