##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Utilities for resizing images.

$Id: utilities.py,v 1.1 2003/08/15 12:10:43 BjornT Exp $
"""

import popen2

from zope.interface import implements
from zope.app.file import Image
from photo.interfaces import IPILImageUtility, IImageMagickUtility

from PIL import Image as PILImage
from cStringIO import StringIO


class PILImageUtility:
    """An image utility which uses PIL.
    """
    implements(IPILImageUtility)

    def resize(self, image, size, keep_aspect=False):
        """See IPILImageResizeUtility"""
        im = PILImage.open(StringIO(image.data))
        fmt = im.format
        new_size = self._getNewSize(image.getImageSize(), size, keep_aspect)
        new_data = StringIO()
        ## avoid a DeprecationWarning by passing integers
        new_size = map(int, new_size)
        (im.resize(new_size)).save(new_data, fmt)
        return Image(new_data.getvalue())

    def _getNewSize(self, image_size, desired_size, keep_aspect):
        """Resizes image_size to desired_size, optionally keeping the
        aspect ratio.
        """
        if keep_aspect:
            x_ratio = float(desired_size[0])/image_size[0]
            y_ratio = float(1.0*desired_size[1])/image_size[1]
            if x_ratio < y_ratio:
                new_size = (round(x_ratio*image_size[0]),
                            round(x_ratio*image_size[1]))
            else:
                new_size = (round(y_ratio*image_size[0]),
                            round(y_ratio*image_size[1]))
            return new_size
        else:
            return desired_size


class ImageMagickUtility:
    """An image utility which uses ImageMagick.

    It needs the convert (or convert.exe) to be in the path.
    """
    implements(IImageMagickUtility)

    def resize(self, image, size, keep_aspect=False):
        """See IImageMacickResizeUtility"""
        instream, outstream = self._getConvertResizePipe(size, keep_aspect)
        outstream.write(image.data)
        outstream.close()
        new_data = StringIO()
        new_data.write(instream.read())
        return Image(new_data.getvalue())

    def _getConvertResizePipe(self, size, keep_aspect):
        """Returns a pipe communicating with the convert program."""
        # XXX this code isn't tested much, may not work on every system
        if keep_aspect:
            convert_call = 'convert -resize %sx%s - -' % size
        else:
            convert_call = 'convert -resize %sx%s! - -' % size
            
        convert = popen2.Popen3(convert_call,
                                True)
        if convert.poll() == -1:
            return popen2.popen2(convert_call, mode='b') 
        else:
            # XXX here we should raise some error since we couldn't find the
            #     convert executable.
            pass
