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
"""The Photo package

$Id: __init__.py,v 1.2 2003/09/21 22:17:47 BjornT Exp $
"""

from zope.interface import implements
from zope.app.container.btree import BTreeContainer
from zope.app.file.image import Image
from zope.app.file.interfaces import IFileContent
from zope.app.filerepresentation.interfaces import IDirectoryFactory, IFileFactory
from zope.app.size.interfaces import ISized
from zope.app.container.interfaces import IContainer
from zope.app.dublincore.interfaces import ICMFDublinCore
from zope.app import zapi
from zope.i18n import MessageIDFactory

from photo.interfaces import IPhoto, IImageResizeUtility
from photo.interfaces import IPhotoContainer

_ = MessageIDFactory("photo")

defaultDisplayIds = {u'thumbnail': (128,128),
                     u'xsmall': (200,200),
                     u'small': (320,320),
                     u'medium': (480,480),
                     u'large': (768,768),
                     u'xlarge': (1024,1024),
                     u'original': (0,0)
                     }

# defaultImageResizer = 'ImageMagick Image Utility'
defaultImageResizer = 'PIL Image Utility'

class Photo(BTreeContainer):

    implements(IPhoto, IContainer, IFileContent)

    # ATTRIBUTES
    useParentOptions = True
    
    # CONSTRUCTOR
    def __init__(self):
        super(Photo, self).__init__()
        self._displayIds = defaultDisplayIds
        self.resizeUtility = defaultImageResizer

    # PROPERTIES
    ## do we need the DC stuff at all? -- ivo
    def getTitle(self):
        """Gets the title of the photo.

        Since we are annotatable we use the title in the dublin core"""
        return ICMFDublinCore(self).title

    def setTitle(self, title):
        """Sets the title of the photo

        Since we are annotatable we use the title in the dublin core"""
        ICMFDublinCore(self).title = title

    title = property(getTitle, setTitle)

    def getDescription(self):
        """Gets the description of the photo

        Since we are annotatable we use the description in the dublin core"""
        return ICMFDublinCore(self).description

    def setDescription(self, description):
        """Sets the description of the photo

        Since we are annotatable we use the description in the dublin core"""
        ICMFDublinCore(self).description = description

    description = property(getDescription, setDescription)

    _data = ''

    def getData(self):
        """Gets the data of the original photo"""
        return self._data

    def setData(self, data):
        """Sets the data of the original photo"""
        self._data = data
        self._deleteGeneratedDisplays()
        im = Image(data)
        self[u'original'] = im
        self._displayIds['original'] = im.getImageSize()

    data = property(getData, setData)

    _currentDisplayId = 'medium'

    def setCurrentDisplayId(self, displayId):
        """Set the current display id, so it's not necessary to specify
        it to getImage() every time.
        """
        if displayId in self.getDisplayIds():
            self._currentDisplayId = displayId

    def getCurrentDisplayId(self):
        """Gets the current display id"""
        return self._getPhotoOption('currentDisplayId')

    currentDisplayId = property(getCurrentDisplayId, setCurrentDisplayId)

    _resizeUtility = defaultImageResizer

    def setResizeUtility(self, val):
        """Sets the resize utility."""
        self._resizeUtility = val

    def getResizeUtility(self):
        """Gets the resize utility."""
        return self._getPhotoOption('resizeUtility')

    resizeUtility = property(getResizeUtility, setResizeUtility)

    # PUBLIC METHODS
    def getDisplayIds(self):
        """See IPhoto"""
        result = self._displayIds.keys()
        result.reverse()
        return result
    
    def getDisplaySize(self, displayId):
        """See IPhoto"""
        if  not self._displayIds.has_key(displayId):
            return None
        else:
            return self._displayIds[displayId]

    def getImage(self, displayId = None):
        """See IPhoto"""
        if not self._data:
            return
        if displayId == None:
            displayId = self.currentDisplayId
        if displayId not in self.getDisplayIds():
            return None
        if not self.__contains__(displayId):
            self._generateDisplay(displayId)

        return self.get(displayId)


    # PRIVATE METHODS
    def _getPhotoOption(self, option):
        """Returns the photo option, considering useParentOptions."""
        if self.useParentOptions:
            pc = zapi.getParent(self)
            if IPhotoContainer.providedBy(pc):
                return getattr(pc, option)
            else:
                return getattr(self, '_' + option)
        else:
            return getattr(self, '_' + option)
        
    def _deleteGeneratedDisplays(self):
        for dispId in self.getDisplayIds():
            if self.__contains__(dispId):
                self.__delitem__(dispId)
        

    def _generateDisplay(self, displayId):
        """Generate a new size of the image"""
        im_size = self._displayIds[displayId]
        resizer = zapi.getUtility(IImageResizeUtility,
                                  self.resizeUtility, self)

        image = resizer.resize(Image(self.data), im_size, keep_aspect=True)
        self[displayId] = image
        

class PhotoSized:

    implements(ISized)

    def __init__(self, photo):
        self._photo = photo

    def sizeForSorting(self):
        """See ISized"""
        image = Image(self._photo.data)
        return ('byte', image.getSize())
        
    def sizeForDisplay(self):
        """See ISized"""
        image = Image(self._photo.data)
        length = len(self._photo.data)
        size = image.getSize() 
        if size <= 0:
            return u''
        else:
            # XXX size should be localized (the formatting of the number)
            if size > 1024*1024:
                size = "%0.02f" % (size / (1024*1024.0))
                unit = _('MB')
            elif size > 1024:
                size = "%0.02f" % (size / 1024.0)
                unit = _('kB')
            else:
                unit = _('bytes')
                
            x, y = image.getImageSize()
            result = '${size} ${unit} ${x}x${y}'
            result = _(result)
            result.mapping = {'size': size, 'unit': unit, 'x': x, 'y': y}
            return result

class PhotoFactory(object):
    """Creates photos in the file system representaion.

    This class can create photos instead of both directories and
    files in the file system representation.
    """

    implements(IDirectoryFactory, IFileFactory)
        
    def __call__(self, name, content_type='', data=None):
        photo = Photo()
        if data:
            photo.data = data
        return photo
        
