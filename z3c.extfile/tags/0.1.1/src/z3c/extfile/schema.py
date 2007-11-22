from zope import schema, interface
from z3c.extfile import interfaces

class ExtBytesField(schema.Bytes):

    interface.implements(interfaces.IExtBytesField)

    def validate(self, value):
        """test if we have a file"""
        return hasattr(value,'seek') and hasattr(value,'read')

