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
"""The Photo Slide package

$Id: __init__.py,v 1.2 2003/09/21 22:18:16 BjornT Exp $
"""

from zope.app import zapi
from zope.app.container.btree import BTreeContainer
from zope.app.folder import Folder
from zope.app.filerepresentation.interfaces import IDirectoryFactory
from zope.interface import implements

from persistent.list import PersistentList

from photo import defaultImageResizer
from photoslide.interfaces import IPhotoSlide, IPhotoSlideFolder

class PhotoSlide(BTreeContainer):
    """An implementation of IPhotoSlide."""

    implements(IPhotoSlide)

    title = ''
    description = ''
    currentDisplayId = 'medium'
    resizeUtility = defaultImageResizer
    useParentOptions = True
    
    def __init__(self, title=''):
        super(PhotoSlide, self).__init__()
        self._title = title
        self._positions = PersistentList()

    def __setitem__(self, key, object):
        """Needed in order to keep track of the positions of the photos."""
        super(PhotoSlide, self).__setitem__(key, object)
        if key not in self._positions:
            self._positions.append(key)
        return key

    def __delitem__(self, key):
        """Needed in order to keep track of the positions of the photos."""
        if key in self._positions:
            self._positions.remove(key)
        super(PhotoSlide, self).__delitem__(key)

    def getPosition(self, photoName):
        """See IPhotoSlide."""
        return self._positions.index(photoName)+1

    def setPosition(self, photoName, index):
        """See IPhotoSlide."""
        self._positions.remove(photoName)
        self._positions.insert(int(index)-1, photoName)

    def getPhotos(self):
        """See IPhotoSlide."""
        photos = []
        for name in self._positions:
            photos.append(self[name])
            
        return photos

    def getPhotoNames(self):
        """See IPhotoSlide."""
        return self._positions

class PhotoSlideFactory(object):
    """Creates photo slides in the file system representation. """

    implements(IDirectoryFactory)

    def __call__(self, name):
        photoslide = PhotoSlide()
        photoslide.title = name
        return photoslide

class PhotoSlideFolder(BTreeContainer):
    """An implementation of IPhotoSlideFolder

    It does nothing special for now.
    """

    implements(IPhotoSlideFolder)
