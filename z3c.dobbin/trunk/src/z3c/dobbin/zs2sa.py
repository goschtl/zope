from zope import schema
import sqlalchemy as rdb

class FieldTranslator( object ):
    """ Translate a zope schema field to an sa  column
    """

    def __init__(self, column_type):
        self.column_type = column_type

    def extractInfo( self, field, info ):
        d = {}
        d['name'] = field.getName()
        if field.required:
            d['nullable'] = False
        d['default'] = field.default
        d['type'] = self.column_type        
        return d
    
    def __call__(self, field, annotation):
        d = self.extractInfo( field, annotation )
        name, type = d['name'], d['type']
        del d['name']
        del d['type']
        return rdb.Column( name, type, **d)

class StringTranslator(FieldTranslator):
    
    column_type = rdb.Text

    def __init__(self, column_type=None):
        self.column_type = column_type or self.column_type
        
    def extractInfo( self, field, info ):
        d = super( StringTranslator, self ).extractInfo( field, info )
        if schema.interfaces.IMinMaxLen.providedBy( field ):
            d['type'].length = field.max_length
        return d

class ObjectTranslator(object):
    
    def __call__(self, field, metadata):
        table = transmute(field.schema, metadata)
        pk = get_pk_name(table.name)
        field_name = "%s.%s" % table.name, pk
        return rdb.Column(pk, rdb.Integer, rdb.ForeignKey(field_name),
            nullable=False)

fieldmap = {
    'ASCII': StringTranslator(),
    'ASCIILine': StringTranslator(),
    'Bool': FieldTranslator(rdb.BOOLEAN),
    'Bytes': FieldTranslator(rdb.BLOB),
    'BytesLine': FieldTranslator(rdb.BLOB),
    'Choice': StringTranslator(),
    'Date': FieldTranslator(rdb.DATE), 
    'Datetime': FieldTranslator(rdb.DATE), 
    'DottedName': StringTranslator(),
    'Float': FieldTranslator(rdb.Float), 
    'Id': StringTranslator(),
    'Int': FieldTranslator(rdb.Integer),
    'Object': ObjectTranslator(),
    'Password': StringTranslator(),
    'SourceText': StringTranslator(),
    'Text': StringTranslator(),
    'TextLine': StringTranslator(),
    'URI': StringTranslator(),
}
