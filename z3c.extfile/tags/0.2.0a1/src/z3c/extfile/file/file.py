from persistent import  Persistent
from z3c.extfile.property import ExtBytesProperty
from interfaces import IExtFile
from zope import interface

class ExtFile(Persistent):

    """A zope file implementation based on z3c.extfile"""

    interface.implements(IExtFile)
    data = ExtBytesProperty('data')
    
    def __init__(self, data='', contentType=''):
        self.data = data
        self.contentType = contentType
        
    def getSize(self):
        return len(self.data)
