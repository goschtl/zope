from zope import schema, interface
from z3c.extfile import interfaces
from zope.schema.interfaces import InvalidValue

class ExtBytesField(schema.Bytes):

    interface.implements(interfaces.IExtBytesField)

    def validate(self, value):
        """test if we have a file"""
        return hasattr(value,'seek') and hasattr(value,'read')
    
