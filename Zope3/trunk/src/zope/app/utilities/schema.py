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

$Id: schema.py,v 1.6 2003/09/24 21:00:40 sidnei Exp $
"""
from persistence.dict import PersistentDict
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.app import zapi
from zope.app.introspector import nameToInterface, interfaceToName
from zope.app.browser.container.adding import Adding
from zope.app.utilities.interfaces import IMutableSchemaContent
from zope.app.interfaces.utilities.schema import \
     ISchemaAdding, IMutableSchema, ISchemaUtility
from zope.app.services.interface import PersistentInterfaceClass
from zope.app.services.interface import PersistentInterface
from zope.app.services.utility import UtilityRegistration
from zope.interface import implements
from zope.interface import directlyProvides, directlyProvidedBy
from zope.schema import getFieldsInOrder, getFieldNamesInOrder
from zope.app.container.contained import Contained, setitem, uncontained

class SchemaUtility(PersistentInterfaceClass):

    implements(IMutableSchema, ISchemaUtility)

    def __init__(self):
        super(SchemaUtility, self).__init__('', (PersistentInterface,))
        self.schemaPermissions = PersistentDict()
        self._InterfaceClass__attrs = PersistentDict()

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
        self._setField(name, field)

    def removeField(self, name):
        """See zope.app.interfaces.utilities.IMutableSchema"""
        fields = getFieldNamesInOrder(self)
        if name not in fields:
            raise KeyError, "Field %s does not exists." % name
        self._delField(name)

    def renameField(self, orig_name, target_name):
        """See zope.app.interfaces.utilities.IMutableSchema"""
        fields = getFieldNamesInOrder(self)
        if orig_name not in fields:
            raise KeyError, "Field %s does not exists." % orig_name
        if target_name in fields:
            raise KeyError, "Field %s already exists." % target_name
        field = self._getField(orig_name)
        self._delField(orig_name)
        self._setField(target_name, field)

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
        self._setField(name, field)
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

    def _getField(self, name):
        return self._InterfaceClass__attrs[name]

    def _setField(self, name, field):
        field = trustedRemoveSecurityProxy(field)
        if not field.__name__:
            field.__name__ = name
        setitem(self, self._InterfaceClass__attrs.__setitem__, name, field)
        self._p_changed = 1

    def _delField(self, name):
        uncontained(self._InterfaceClass__attrs[name], self, name)
        del self._InterfaceClass__attrs[name]
        self._p_changed = 1

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
