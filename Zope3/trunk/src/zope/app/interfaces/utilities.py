from zope.interface import Interface
from zope.interface.interfaces import IInterface
from zope.schema import TextLine

class ISchemaUtility(Interface):

    name = TextLine(title=u'Schema Name',
                    description=u"Schema Name")

class IMutableSchema(IInterface):

    def addField(name, field):
        """Add a field to schema.
        """

    def removeField(name):
        """Remove field from schema.
        """

    def renameField(orig_name, target_name):
        """Rename field.
        """

    def insertField(name, field, position):
        """Insert a field at position.
        """

    def moveField(name, position):
        """Move field to position.
        """
