##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""TTW Schema (as Utility)

$Id: schema.py,v 1.9 2003/10/08 13:16:01 sidnei Exp $
"""
from types import FunctionType

from persistence.dict import PersistentDict
from persistence.wrapper import Struct

from zope.security.proxy import trustedRemoveSecurityProxy
from zope.interface import Interface
from zope.interface import implements
from zope.interface import directlyProvides, directlyProvidedBy
from zope.app import zapi
from zope.app.introspector import nameToInterface, interfaceToName
from zope.app.browser.container.adding import Adding
from zope.app.utilities.interfaces import IMutableSchemaContent
from zope.app.interfaces.utilities.schema import \
     ISchemaAdding, IMutableSchema, ISchemaUtility
from zope.app.services.interface import PersistentInterfaceClass
from zope.app.services.utility import UtilityRegistration
from zope.schema import getFieldsInOrder, getFieldNamesInOrder
from zope.app.container.contained import Contained, setitem, uncontained
from zope.interface.interface import Attribute, Method, fromFunction
from zope.interface.interface import InterfaceClass
from zope.interface.exceptions import InvalidInterface

class SchemaUtility(PersistentInterfaceClass, Contained):

    implements(IMutableSchema, ISchemaUtility)

    def __init__(self, name='', bases=(), attrs=None,
                 __doc__=None, __module__=None):
        if not bases:
            bases = (Interface,)
        super(SchemaUtility, self).__init__(name, bases,
                                            attrs, __doc__, __module__)
        self.schemaPermissions = PersistentDict()
        self._attrs = PersistentDict()

    def setName(self, name):
        """See zope.app.interfaces.utilities.IMutableSchema"""
        self.__name__ = name

    def addField(self, name, field):
        """See zope.app.interfaces.utilities.IMutableSchema"""
        fields = getFieldsInOrder(self)
        field_names = [n for n, f in fields]
        fields = [f for n, f in fields]
        if name in field_names:
            raise KeyError, "Field %s already exists." % name
        if fields:
            field.order = fields[-1].order + 1
        self[name] = field

    def removeField(self, name):
        """See zope.app.interfaces.utilities.IMutableSchema"""
        fields = getFieldNamesInOrder(self)
        if name not in fields:
            raise KeyError, "Field %s does not exists." % name
        del self[name]

    def renameField(self, orig_name, target_name):
        """See zope.app.interfaces.utilities.IMutableSchema"""
        fields = getFieldNamesInOrder(self)
        if orig_name not in fields:
            raise KeyError, "Field %s does not exists." % orig_name
        if target_name in fields:
            raise KeyError, "Field %s already exists." % target_name
        field = self[orig_name]
        del self[orig_name]
        self[target_name] = field

    def insertField(self, name, field, position):
        """See zope.app.interfaces.utilities.IMutableSchema"""
        fields = getFieldsInOrder(self)
        field_names = [n for n, f in fields]
        fields = [f for n, f in fields]
        if name in field_names:
            raise KeyError, "Field %s already exists." % name
        if not 0 <= position <= len(field_names):
            raise IndexError, "Position %s out of range." % position
        if fields and position > 0:
            field.order = fields[position-1].order + 1
        else:
            field.order = 1
        self[name] = field
        for field in fields[position:]:
            field.order += 1

    def moveField(self, name, position):
        """See zope.app.interfaces.utilities.IMutableSchema"""
        fields = getFieldsInOrder(self)
        field_names = [n for n, f in fields]
        fields = [f for n, f in fields]
        if name not in field_names:
            raise KeyError, "Field %s does not exist." % name
        if not 0 <= position <= len(field_names):
            raise IndexError, "Position %s out of range." % position
        index = field_names.index(name)
        field = fields[index]
        field.order = fields[position-1].order + 1
        for field in fields[position:]:
            field.order += 1

    def __delitem__(self, name):
        uncontained(self._attrs[name], self, name)
        del self._attrs[name]

    def __setitem__(self, name, value):
        value = trustedRemoveSecurityProxy(value)
        if isinstance(value, Attribute):
            value.interface = name
            if not value.__name__:
                value.__name__ = name
            elif isinstance(value, FunctionType):
                attrs[name] = fromFunction(value, name, name=name)
            else:
                raise InvalidInterface("Concrete attribute, %s" % name)
        value = Struct(value)
        setitem(self, self._attrs.__setitem__, name, value)

    # Methods copied from zope.interface.interface.InterfaceClass,
    # to avoid having to work around name mangling, which happens to be
    # ugly and undesirable.
    # Copied some methods, but not all. Only the ones that used __attrs
    # and __bases__. Changed __attrs to _attrs, which is a PersistentDict,
    # and __bases__ to getBases(), whic filters instances of InterfaceClass
    def getBases(self):
        return [b for b in self.__bases__ if isinstance(b, self.__class__)]

    def extends(self, other, strict=True):
        """Does an interface extend another?"""
        if not strict and self == other:
            return True

        for b in self.getBases():
            if b == other: return True
            if b.extends(other): return True
        return False

    def names(self, all=False):
        """Return the attribute names defined by the interface."""
        if not all:
            return self._attrs.keys()

        r = {}
        for name in self._attrs.keys():
            r[name] = 1
        for base in self.getBases():
            for name in base.names(all):
                r[name] = 1
        return r.keys()

    def namesAndDescriptions(self, all=False):
        """Return attribute names and descriptions defined by interface."""
        if not all:
            return self._attrs.items()

        r = {}
        for name, d in self._attrs.items():
            r[name] = d

        for base in self.getBases():
            for name, d in base.namesAndDescriptions(all):
                if name not in r:
                    r[name] = d

        return r.items()

    def getDescriptionFor(self, name):
        """Return the attribute description for the given name."""
        r = self.queryDescriptionFor(name)
        if r is not None:
            return r

        raise KeyError, name

    __getitem__ = getDescriptionFor

    def queryDescriptionFor(self, name, default=None):
        """Return the attribute description for the given name."""
        r = self._attrs.get(name, self)
        if r is not self:
            return r
        for base in self.getBases():
            r = base.queryDescriptionFor(name, self)
            if r is not self:
                return r

        return default

    get = queryDescriptionFor

    def deferred(self):
        """Return a defered class corresponding to the interface."""
        if hasattr(self, "_deferred"): return self._deferred

        klass={}
        exec "class %s: pass" % self.__name__ in klass
        klass=klass[self.__name__]

        self.__d(klass.__dict__)

        self._deferred=klass

        return klass

    def __d(self, dict):

        for k, v in self._attrs.items():
            if isinstance(v, Method) and not (k in dict):
                dict[k]=v

        for b in self.getBases(): b.__d(dict)

class SchemaAdding(Adding):

    implements(ISchemaAdding)

    menu_id = "add_schema_field"

    def add(self, content):
        name = self.contentName
        container = zapi.getAdapter(self.context, IMutableSchema)
        container.addField(name, content)
        return content

    def nextURL(self):
        """See zope.app.interfaces.container.IAdding"""
        return (str(zapi.getView(self.context, "absolute_url", self.request))
                + '/@@editschema.html')


class SchemaRegistration(UtilityRegistration):
    """Schema Registration

    We have a custom registration here, since we want active registrations to
    set the name of the schema.
    """

    def activated(self):
        schema = self.getComponent()
        schema.setName(self.name)

    def deactivated(self):
        schema = self.getComponent()
        schema.setName('<schema not activated>')


# XXX: This needs refactoring
class MutableSchemaContent(Contained):

    implements(IMutableSchemaContent)

    schema_id = None

    def _set_schema(self, iface):
        directlyProvides(self, iface)
        self.schema_id = interfaceToName(self, iface)

    def _get_schema(self):
        provided = list(directlyProvidedBy(self))
        schema = self.schema_id and \
                 nameToInterface(self, self.schema_id) or None
        if not schema in provided and schema is not None:
            directlyProvides(self, schema)
        return schema or provided and provided[0] or None

    mutableschema = property(_get_schema, _set_schema)
