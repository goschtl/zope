##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Type Reprsentation Registry

$Id$
"""
from zope.interface import implements, providedBy
import zope.schema

from interfaces import ITypeRepresentation

class TypeRepresentationRegistry:
    def __init__(self, default):
        self._registry = {}
        self._default = default

    #def registerType(self, type, factory):
    #    self._registry[type] = factory

    def represent(self, object):
        # returns an ITypeRepresentation object
        factory = self._registry.get(type(object))
        if factory is not None:
            return factory(object)
        return self._default(object)

    def register(self, representation):
        for type in representation.getTypes():
            self._registry[type] = representation

class DefaultTypeRepresentation:
    implements(ITypeRepresentation)

    def __init__(self, object):
        self.text = repr(object)
        import_name = type(object).__name__
        import_module = type(object).__module__
        if import_module != '__builtin__':
            self.importList = [(import_module, import_name)]
        else:
            self.importList = []

    def getTypes():
        return ()
    getTypes = staticmethod(getTypes)

class DatetimeRepresentation:
    implements(ITypeRepresentation)

    def __init__(self, dt):
        r = repr(dt)
        assert r.startswith('datetime.')
        self.text = r[9:]
        self.importList = [('datetime', type(dt).__name__)]

    def getTypes():
        import datetime
        # XXX not supporting timedelta yet
        return [
            datetime.date,
            datetime.datetime,
            datetime.time,
          #  datetime.timedelta,
        ]
    getTypes = staticmethod(getTypes)

class DefaultFieldRepresentation:
    implements(ITypeRepresentation)

    def __init__(self, field):
        # This field is described by a schema, or schemas, as found by
        # providedBy. The fields of this field's schema are
        # its properties -- that is, the things we give as arguments when
        # constructing this field.
        # We're going to get these properties, get source-code
        # representations of them, and sort out appropriate imports.
        names = {} # used as set of property names, ignoring values
        for interface in providedBy(field):
            names.update(zope.schema.getFields(interface))
        # getFields only returns data for Fields in the interface.
        # Otherwise, it returns an empty dict.

        # At this point, name_property is a dict with keys of the
        # property names, and values of property objects.
        # XXX I don't know if we're following proper MRO though.

        global typeRegistry
        self.importList =  self._getImportList(field)
        arguments = []
        # don't represent order of this field within its schema,
        # as that will be implicit
        if 'order' in names:
            del names['order']
        # we want to order the field constructor arguments according to the
        # order of the fields on the schema describing this field
        propertysorter = lambda x, y: cmp(x[1].order, y[1].order)
        names_items = names.items()
        names_items.sort(propertysorter)
        # make a representation of property value and collect necessary imports
        # we are not interested in the property field itself, just
        # property value
        for name, property in names_items:
            value = getattr(field, name)
            if property.default == value:
                continue
            representation = typeRegistry.represent(value)
            arguments.append((name, representation.text))
            for import_spec in representation.importList:
                self.importList.append(import_spec)

        arguments_text = ', '.join(["%s=%s" % item for item in arguments])

        self.text = "%s(%s)" % (type(field).__name__, arguments_text)

    def getTypes():
        return ()
    getTypes = staticmethod(getTypes)

    def _getImportList(field):
        field_class = type(field)
        if getattr(zope.schema, field_class.__name__, None) is field_class:
            module_name = 'zope.schema'
        else:
            module_name = field_class.__module__
        return [(module_name, field_class.__name__)]

    _getImportList = staticmethod(_getImportList)

typeRegistry = TypeRepresentationRegistry(DefaultTypeRepresentation)
typeRegistry.register(DatetimeRepresentation)

fieldRegistry = TypeRepresentationRegistry(DefaultFieldRepresentation)
