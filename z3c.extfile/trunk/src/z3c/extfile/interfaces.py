from zope import interface, schema
from zope.schema.interfaces import IBytes

class IHashDir(interface.Interface):

    """a hashdir utility"""

    path = schema.TextLine(title=u"Path")
    
class IExtBytesField(IBytes):

    """A field holding Bytes in external files"""

class IFile(interface.Interface):

    """marker for file objects"""

class IReadFile(IFile):

    """a readonly file"""

    digest = schema.ASCII(title=u'Digest', readonly=True)
    closed = schema.Bool(title=u'Closed', readonly=True)

    def __len__():
        """returns the length/size of file"""

    def seek(offset, whence=0):
        """see file.seek"""

    def tell():
        """see file.tell"""

    def read(size):
        """see file.read"""

    def close():
        """see file.close"""

    def __iter__():
        """see file.__iter__"""

class IWriteFile(IFile):

    def write(s):

        """writes s to file"""

    def commit():

        """commits the file to be stored with the digest"""

    

