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
"""Interface descriptions for the Photo package

$Id: interfaces.py,v 1.3 2003/11/21 22:06:50 BjornT Exp $
"""

from zope.app.container.interfaces import IContainer
from zope.app.servicenames import Utilities
from zope.component import getService, ComponentLookupError
from zope.interface import Interface, Attribute
from zope.schema import Text, TextLine, Bytes, Choice, Bool
from zope.i18n import MessageIDFactory

_ = MessageIDFactory("photo")


dispIds = [u'thumbnail',
           u'xsmall',
           u'small',
           u'medium',
           u'large',
           u'xlarge',
           u'original'
           ]

class ResizeUtilityName(TextLine):
    """Field which lists all available resize utilities."""
    
    def __allowed(self):
        """Finds all resize utility names and returns them.
        
        Note that this method works only if the Field is context wrapped.
        """
        resizeUtilities = []
        try:
            us = getService(self.context, Utilities)
            for resize_util_reg in us.getUtilitiesFor(IImageResizeUtility):
                resizeUtilities.append(resize_util_reg[0])
        except ComponentLookupError:
            resizeUtilities = []
        return resizeUtilities

    allowed_values = property(__allowed)

class IPhotoFolder(IContainer):
    """Marker interface in order to make it easier to upload photos.

    If a container is marked with this interface it will create 
    photos when an images are uploaded in it.
    """

class IPhotoContainer(Interface):
    """Schema for certain photo options.
    
    Objects that will contain photos should implement this schema.
    """
    
    useParentOptions = Bool(
        title=_('Use Parent Options'),
        description=
        _("If inside a photo container, ignore the following options."),
        default=True,
        required=True
        )

    currentDisplayId = Choice(
        title=_('Default Size'),
        description=_('The defualt size of the photo(s).'),
        values=dispIds,
        default=u'medium',
        required=True
        )

    resizeUtility = ResizeUtilityName(
        title=_('Resize Utility'),
        description=_('The utility used for resizing the images'),
        required=True
        )


class IPhoto(IContainer, IPhotoContainer):
    """Provides several sizes of an Image.
    """

    title = TextLine(title=_('Title'),
                     description=_('The title of the photo'),
                     default=u'',
                     required=False)

    description = Text(title=_('Description'),
                       description=_('The description of the photo'),
                       default=u'',
                       required=False)
                               
    data = Bytes(title=_('Image File'),
                 description=_('The original image'),
                 required=True)

    def getDisplayIds():
        """Gets a list of available display ids"""

    def getDisplaySize(dispId):
        """Gets the geometry of the specified display id"""

    def getImage(dispId):
        """Returns the image of the specified display id"""
        

class IImageResizeUtility(Interface):
    """Resizes an given image to a give size"""

    def resize(image, size, keep_aspect):
        """Returns a new image resized to the given size

        If keep_aspect is true the image should be resized as close
        as possible to size while retaining its aspect ratio.
        """

class IPILImageUtility(IImageResizeUtility):
    """An image utility using PIL.

    For now it only resizes images.
    """

class IImageMagickUtility(IImageResizeUtility):
    """An image utility using ImageMagick.

    For now it only resizes images.
    """
