from zope import component, interface
import interfaces
from cStringIO import StringIO

_marker = object()
BLOCK_SIZE = 1024*128

class ExtBytesProperty(object):

    """a property which's values are stored as external files"""

    def __init__(self, name):
        self.__name = name

    @property
    def hd(self):
        return component.getUtility(interfaces.IHashDir)
    
    def __get__(self, inst, klass):
        if inst is None:
            return self
        digest = inst.__dict__.get(self.__name, _marker)
        if digest is _marker:
            return None
        return self.hd.open(digest)

    def __set__(self, inst, value):
        # ignore if value is None
        if value is None:
            return
        # Handle case when value is a string
        if isinstance(value, unicode):
            value = value.encode('UTF-8')
        if isinstance(value, str):
            value = StringIO(value)
        value.seek(0)
        f = self.hd.new()
        while True:
            chunk = value.read(BLOCK_SIZE)
            if not chunk:
                digest = f.commit()
                inst.__dict__[self.__name] = digest
                break
            f.write(chunk)


