from zope.interface import implements
from zope.app.services.interface import PersistentInterfaceClass
from zope.app.interfaces.utilities import IMutableSchema
from zope.schema import getFieldsInOrder, getFieldNamesInOrder

class SchemaUtility(PersistentInterfaceClass):

    implements(IMutableSchema)

    def addField(self, name, field):
        """Add a field to schema.
        """
        fields = getFieldNamesInOrder(self)
        if name in fields:
            raise KeyError, "Field %s already exists." % name
        self._setField(name, field)
        self._p_changed = 1

    def removeField(self, name):
        """Remove field from schema.
        """
        fields = getFieldNamesInOrder(self)
        if name not in fields:
            raise KeyError, "Field %s does not exists." % name
        self._delField(name)
        self._p_changed = 1

    def renameField(self, orig_name, target_name):
        """Rename field.
        """
        fields = getFieldNamesInOrder(self)
        if orig_name not in fields:
            raise KeyError, "Field %s does not exists." % orig_name
        if target_name in fields:
            raise KeyError, "Field %s already exists." % target_name
        field = self._getField(orig_name)
        self._delField(orig_name)
        self._setField(target_name, field)
        self._p_changed = 1

    def insertField(self, name, field, position):
        """Insert a field at position.
        """
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
        self._p_changed = 1

    def moveField(self, name, position):
        """Move field to position.
        """
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
        self._p_changed = 1

    def _getField(self, name):
        return self._InterfaceClass__attrs[name]

    def _setField(self, name, field):
        self._InterfaceClass__attrs[name] = field

    def _delField(self, name):
        del self._InterfaceClass__attrs[name]
