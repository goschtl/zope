from zope.interface import Interface, Attribute
from zope.schema.interfaces import IField
from zope.schema import TextLine, Bytes

class IFile(IField):
    u"""File field."""

class IHurryFile(Interface):
    filename = TextLine(title=u'Filename of file')
    data = Bytes(title=u'Data in file')
    file = Attribute('File-like object with data')
    headers = Attribute('Headers associated with file')

class IFileRetrieval(Interface):
    def getFile(data):
        """Get a file object for file data.
        """

    def createFile(filename, f):
        """Given a file object, create a HurryFile with that data in it.
        """
