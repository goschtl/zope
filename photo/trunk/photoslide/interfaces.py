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
"""Interface descriptions for the PhotoSlide package

$Id: interfaces.py,v 1.1 2003/08/15 12:15:14 BjornT Exp $
"""
from zope.schema import TextLine, Text
from zope.app.container.interfaces import IContainer
from zope.i18n import MessageIDFactory

from photo.interfaces import IPhotoContainer

_ = MessageIDFactory("photo")


class IPhotoSlide(IContainer, IPhotoContainer):
    """Contains Photo objects and can show a slide show of them"""

    title = TextLine(title=_('Title'),
                     description=_('The title of the photo slide'),
                     default=u'',
                     required=True)

    description = Text(title=_('Description'),
                       description=_('The description of the photo slide'),
                       default=u'',
                       required=False)


    def getPosition(photo):
        """Returns the position of the photo in the slide show.

        The first photo has position 1.
        """
    
    def setPosition(photo, index):
        """Sets the position of the photo in the slide show."""

    def getPhotos():
        """Returns an ordered list of the photos."""

    def getPhotoNames():
        """Returns an ordered list of the names of the photos."""

class IPhotoSlideFolder(IContainer):
    """A container which contains PhotoSlide objects.

    For now it's only used in order to make it easier to create new
    slide shows. In future it will probably have to keep track of the
    order of the slide shows and it's implementation should provide
    a nice view of the available shows.
    """
    
