##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""IPhoto implementations

$Id: __init__.py,v 1.1.1.1 2004/02/18 18:07:08 srichter Exp $
"""
from persistent.dict import PersistentDict
from zope.interface import implements
from zope.schema import getFieldNames
from zope.app.annotation.interfaces import IAnnotations
from zope.app.file.interfaces import IImage
from interfaces import IPhoto, photodavns


class ImagePhotoNamespace(object):
    """Implement IPhoto namespace for IImage.

    Examples:

    >>> from zope.app.file.image import Image
    >>> image = Image()
    >>> photo = IPhoto(image)
    
    >>> photo.height is None
    True
    >>> photo.height = 768
    >>> photo.height
    768
    >>> photo.height = u'100'
    Traceback (most recent call last):
    ...
    WrongType: (u'100', (<type 'int'>, <type 'long'>))
    
    >>> photo.width is None
    True
    >>> photo.width = 1024
    >>> photo.width
    1024
    
    >>> photo.equivalent35mm is None
    True
    >>> photo.equivalent35mm = u'41 mm'
    >>> photo.equivalent35mm
    u'41 mm'
    
    >>> photo.aperture is None
    True
    >>> photo.aperture = u'f/2.8'
    >>> photo.aperture
    u'f/2.8'
    
    >>> photo.exposureTime is None
    True
    >>> photo.exposureTime = 0.031
    >>> photo.exposureTime
    0.031
    
    >>> photo.occasion
    Traceback (most recent call last):
    ...
    AttributeError: 'ImagePhotoNamespace' object has no attribute 'occasion'
    """

    implements(IPhoto)
    __used_for__ = IImage

    def __init__(self, context):
        self.context = context
        self._annotations = IAnnotations(context)
        if not self._annotations.get(photodavns):
            self._annotations[photodavns] = PersistentDict()

    def __getattr__(self, name):
        if not name in getFieldNames(IPhoto):
            raise AttributeError, "'%s' object has no attribute '%s'" %(
                self.__class__.__name__, name)
        #    return super(ImagePhotoNamespace, self).__getattribute__(name)
        return self._annotations[photodavns].get(name, None)

    def __setattr__(self, name, value):
        if not name in getFieldNames(IPhoto):
            return super(ImagePhotoNamespace, self).__setattr__(name, value)
        field = IPhoto[name]
        field.validate(value)
        self._annotations[photodavns][name] = value
