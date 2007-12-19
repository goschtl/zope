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
"""

$Id$
"""
from zope import interface, schema
from zope.size.interfaces import ISized
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class MagicError(Exception):
    pass


class MagicTestError(MagicError):
    pass


class OffsetError(MagicError): 
    pass


class MagicFileError(MagicError): 
    pass


class IMimetypeType(interface.interfaces.IInterface):
    """ mimetype type """


class IFileType(interface.Interface):

    contentType = schema.TextLine(title = u'Content Type')


class IFileTypeModifiedEvent(IObjectModifiedEvent):
    """This event is fired when the filetypes change on an object"""


class ITypeableFile(interface.Interface):
    """A file object that is typeable"""

    data = interface.Attribute('Data of the file')


class IImageSized(ISized):

    def getImageSize():
        """ return width, height of image """
