import os
import stat
import tempfile

from zope import interface

from zope.app.file.interfaces import IImage

LengthError = (TypeError, AttributeError)


class VImage(object):

    """a non persistent image implementation"""

    interface.implements(IImage)

    def __init__(self, contentType='', size=(0, 0)):
        self.data = tempfile.TemporaryFile(prefix='z3c.vimage')
        self.contentType = contentType
        self.size = size
                 
    def getSize(self):
        try:
            return len(self.data)
        except LengthError:
            data = self.data
            if hasattr(data, 'fileno'):
                return int(os.fstat(data.fileno())[stat.ST_SIZE])
        pos = self.data.tell()
        size = len(data.read())
        data.seek(pos)
        return size

    def getImageSize(self):
        return self.size
    
