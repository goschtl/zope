##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: image.py,v 1.8 2003/06/07 06:37:23 stevea Exp $
"""
import struct
from zope.app.content.file import File
from cStringIO import StringIO
from zope.app.interfaces.content.image import IImage
from zope.app.interfaces.size import ISized
from zope.app.size import byteDisplay

from zope.app.content_types import guess_content_type
from zope.interface import implements

__metaclass__ = type

class Image(File):
    implements(IImage)

    def __init__(self, data=''):
        '''See interface IFile'''
        self.contentType, self._width, self._height = getImageInfo(data)
        self.data = data

    def setData(self, data):
        super(Image, self).setData(data)

        contentType = None
        contentType, self._width, self._height = getImageInfo(self.data)
        if contentType:
            self.contentType = contentType

    def getImageSize(self):
        '''See interface IImage'''
        return (self._width, self._height)

    data = property(File.getData, setData, None,
                    """Contains the data of the file.""")


class ImageSized:

    implements(ISized)

    def __init__(self, image):
        self._image = image

    def sizeForSorting(self):
        'See ISized'
        return ('byte', self._image.getSize())

    def sizeForDisplay(self):
        'See ISized'
        w, h = self._image.getImageSize()
        if w < 0:
            w = '?'
        if h < 0:
            h = '?'
        bytes = self._image.getSize()
        return '%s %sx%s' % (byteDisplay(bytes), w, h)

def getImageInfo(data):
    data = str(data)
    size = len(data)
    height = -1
    width = -1
    content_type = ''

    # handle GIFs
    if (size >= 10) and data[:6] in ('GIF87a', 'GIF89a'):
        # Check to see if content_type is correct
        content_type = 'image/gif'
        w, h = struct.unpack("<HH", data[6:10])
        width = int(w)
        height = int(h)

    # See PNG v1.2 spec (http://www.cdrom.com/pub/png/spec/)
    # Bytes 0-7 are below, 4-byte chunk length, then 'IHDR'
    # and finally the 4-byte width, height
    elif ((size >= 24) and data.startswith('\211PNG\r\n\032\n')
          and (data[12:16] == 'IHDR')):
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[16:24])
        width = int(w)
        height = int(h)

    # Maybe this is for an older PNG version.
    elif (size >= 16) and data.startswith('\211PNG\r\n\032\n'):
        # Check to see if we have the right content type
        content_type = 'image/png'
        w, h = struct.unpack(">LL", data[8:16])
        width = int(w)
        height = int(h)

    # handle JPEGs
    elif (size >= 2) and data.startswith('\377\330'):
        content_type = 'image/jpeg'
        jpeg = StringIO(data)
        jpeg.read(2)
        b = jpeg.read(1)
        try:
            while (b and ord(b) != 0xDA):
                while (ord(b) != 0xFF): b = jpeg.read(1)
                while (ord(b) == 0xFF): b = jpeg.read(1)
                if (ord(b) >= 0xC0 and ord(b) <= 0xC3):
                    jpeg.read(3)
                    h, w = struct.unpack(">HH", jpeg.read(4))
                    break
                else:
                    jpeg.read(int(struct.unpack(">H", jpeg.read(2))[0])-2)
                b = jpeg.read(1)
            width = int(w)
            height = int(h)
        except struct.error:
            pass
        except ValueError:
            pass

    return content_type, width, height


class FileFactory:

    def __init__(self, context):
        self.context = context

    def __call__(self, name, content_type, data):
        if not content_type and data:
            content_type, width, height = getImageInfo(data)
        if not content_type:
            content_type, encoding = guess_content_type(name, data, '')

        if content_type.startswith('image/'):
            return Image(data)

        return File(data, content_type)
