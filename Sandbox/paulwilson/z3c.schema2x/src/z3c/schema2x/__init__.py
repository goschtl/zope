from zope.interface import Interface


class ISchemaSerializer(Interface):
    """
    Schema Serializers provide functions that
    serialize and deserialize object trees according
    to the schema definitions supplied in their 
    interfaces.
    """
