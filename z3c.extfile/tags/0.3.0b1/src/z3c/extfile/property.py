from zope import component
import interfaces
from cStringIO import StringIO

from datamanager import getFile, _storage

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
        return getFile(digest)

    def __set__(self, inst, value):
        # ignore if value is None
        if value is None:
            if inst.__dict__.has_key(self.__name):
                del inst.__dict__[self.__name]
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
                newDigest = f.commit()
                oldDigest = inst.__dict__.get(self.__name, _marker)
                if newDigest == oldDigest:
                    # we have no change, so we have to seek to zero
                    # because this is normal behaviour when setting a
                    # new value
                    if hasattr(_storage, 'dataManager'):
                        if newDigest in _storage.dataManager.files:
                            f = _storage.dataManager.files[newDigest]
                            f.seek(0)
                else:
                    inst.__dict__[self.__name] = newDigest
                break
            f.write(chunk)


