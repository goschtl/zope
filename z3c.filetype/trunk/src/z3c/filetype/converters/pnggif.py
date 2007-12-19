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
""" GIF -> PNG and PNG - > GIF converters

$Id$
"""
from zope import component
from z3c.filetype.interfaces import filetypes
from z3c.filetype.converters.utils import log
from z3c.filetype.converters.pilimage import PILImageConverter

import PIL.Image

# check encoders
try:
    PIL.Image.core.gif_decoder
    PIL.Image.core.gif_encoder
    PIL.Image.core.png_decoder
    PIL.Image.core.png_encoder
except:
    log("PNG/GIF converters are not available. PIL doesn't support this formats")
    raise ImportError()


class PNGtoGIFConverter(PILImageConverter):
    component.adapts(filetypes.IPNGFile, filetypes.IGIFFile)

    _from_format = 'png'
    _dest_format = 'gif'


class GIFtoPNGConverter(PILImageConverter):
    component.adapts(filetypes.IGIFFile, filetypes.IPNGFile)
    
    _from_format = 'gif'
    _dest_format = 'png'
