import zope.i18nmessageid

from zope.size.interfaces import ISized

from zope.size import byteDisplay
from interfaces import filetypes
from zope import component, interface
import os
import stat
import struct


_ = zope.i18nmessageid.MessageFactory("zope")


class ImageFileSized(object):

    interface.implements(ISized)
    
    def __init__(self, image):
        self._image = image

    @property
    def bytes(self):
        try:
            return len(self._image.data)
        except TypeError:
            data = self._image.data
            return int(os.fstat(data.fileno())[stat.ST_SIZE])
        raise NotImplementedError
    
    def sizeForSorting(self):
        '''See `ISized`'''
        return ('byte', self.bytes)

    def getImageSize(self):
        raise NotImplementedError

    def sizeForDisplay(self):
        '''See `ISized`'''

        w, h = self.getImageSize()
        if w < 0:
            w = '?'
        if h < 0:
            h = '?'
        byte_size = byteDisplay(self.bytes)
        mapping = byte_size.mapping
        if mapping is None:
            mapping = {}
        mapping.update({'width': str(w), 'height': str(h)})
        #TODO the way this message id is defined, it won't be picked up by
        # i18nextract and never show up in message catalogs
        return _(byte_size + ' ${width}x${height}', mapping=mapping)


class GIFFileSized(ImageFileSized):

    interface.implements(ISized)
    component.adapts(filetypes.IGIFFile)

    def getImageSize(self):
        data = self._image.data
        data.seek(0)
        data = data.read(24)
        size = len(data)
        width = -1
        height = -1
        if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
            # Check to see if content_type is correct
            w, h = struct.unpack("<HH", data[6:10])
            width = int(w)
            height = int(h)
        return width, height
    
class PNGFileSized(ImageFileSized):

    interface.implements(ISized)
    component.adapts(filetypes.IPNGFile)
    
    def getImageSize(self):
        data = self._image.data
        data.seek(0)
        data = data.read(24)
        size = len(data)
        height = -1
        width = -1
        # See PNG 2. Edition spec (http://www.w3.org/TR/PNG/)
        # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
        # and finally the 4-byte width, height
        if ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
            and (data[12:16] == 'IHDR')):
            w, h = struct.unpack(">LL", data[16:24])
            width = int(w)
            height = int(h)
        # Maybe this is for an older PNG version.
        elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
            w, h = struct.unpack(">LL", data[8:16])
            width = int(w)
            height = int(h)
        return width, height

class JPGFileSized(ImageFileSized):

    interface.implements(ISized)
    component.adapts(filetypes.IJPGFile)
    
    def getImageSize(self):
        data = self._image.data
        data.seek(2)
        size = self.bytes
        height = -1
        width = -1
        b = data.read(1)
        try:
            w = -1
            h = -1
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF): b = data.read(1)
                while (ord(b) == 0xFF): b = data.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    data.read(3)
                    h, w = struct.unpack(">HH", data.read(4))
                    break
                else:
                    data.read(int(struct.unpack(">H", data.read(2))[0])-2)
                b = data.read(1)
            width = int(w)
            height = int(h)
        except struct.error:
            pass
        except ValueError:
            pass
        return width, height
