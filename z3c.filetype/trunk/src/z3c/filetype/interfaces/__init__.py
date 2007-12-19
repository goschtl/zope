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
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class IMimetypeType(interface.interfaces.IInterface):
    """ mimetype type """


class IContentType(interface.Interface):

    contentType = schema.TextLine(
        title = u'Content Type')


class IFileData(interface.Interface):

    def open(mode='r'):
        """ Open file, returns file(-like) object for handling the data """


class IImageSized(ISized):

    def getImageSize():
        """ return width, height of image """


class ITypeableFile(interface.Interface):
    """A file object that is typeable"""

    data = interface.Attribute('Data of the file')


class IFileTypeModifiedEvent(IObjectModifiedEvent):
    """This event is fired when the filetypes change on an object"""


class FileTypeModifiedEvent(ObjectModifiedEvent):
    interface.implements(IFileTypeModifiedEvent)
