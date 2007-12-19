##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" PIL based image converter

$Id$
"""
from cStringIO import StringIO

from zope import interface
from z3c.filetype.interfaces import IFileData
from z3c.filetype.interfaces.converter import \
    ISimpleImageConverter, ConverterException
from z3c.filetype.converters.utils import log

try:
    import PIL.Image
except:
    log("Python Imaging library is not available.")
    raise


class PILImageConverter(object):
    interface.implements(ISimpleImageConverter)

    _from_format = 'raw'
    _dest_format = 'raw'

    def __init__(self, context, destination):
        self.context = context
        self.destination = destination

    def convert(self, width=None, height=None, scale=0, quality=88):
        """ convert image """
        file = IFileData(self.context, None)
        if file is None:
            raise ConverterException("Can't get data from context.")
        
        data = file.open('r')
        try:
            image = PIL.Image.open(data)

            if image.mode == '1':
                image = image.convert('L')
            elif image.mode == 'P':
                image = image.convert('RGBA')

            # get width, height
            orig_size = image.size
            if width is None: width = orig_size[0]
            if height is None: height = orig_size[1]
        
            # Auto-scaling support
            if scale:
                width =  int(round(int(width) * scale))
                height = int(round(int(height) * scale))

            #convert image
            pilfilter = PIL.Image.NEAREST
            if PIL.Image.VERSION >= "1.1.3":
                pilfilter = PIL.Image.ANTIALIAS

            image.thumbnail((width, height), pilfilter)

            newfile = StringIO()
            image.save(newfile, self._dest_format, quality=quality)
            self.destination.data = newfile.getvalue()
        except Exception, e:
            data.close()
            raise ConverterException(str(e))

        data.close()
