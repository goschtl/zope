##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""this module implements the flickr.photos namespace

http://www.flickr.com/services/api/

$Id$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.schema
from zope.schema import fieldproperty
from lovely.flickr import interfaces, flickr


class Photos(list):
    zope.interface.implements(interfaces.IPhotos)

    page = fieldproperty.FieldProperty(interfaces.IPhotos['page'])
    pages = fieldproperty.FieldProperty(interfaces.IPhotos['pages'])
    perpage = fieldproperty.FieldProperty(interfaces.IPhotos['perpage'])
    total = fieldproperty.FieldProperty(interfaces.IPhotos['total'])

    def __init__(self, page, pages, perpage, total):
        super(Photos, self).__init__()
        self.page = page
        self.pages = pages
        self.perpage = perpage
        self.total = total

    @classmethod
    def fromElement(self, element):
        """See interfaces.IBaseFlickrObject"""
        args = dict([
            (name, field.fromUnicode(element.get(name)))
            for name, field in zope.schema.getFields(interfaces.IPhotos).items()
            ])
        photos = Photos(**args)
        for child in element.getchildren():
            photos.append(Photo.fromElement(child))
        return photos

    def __repr__(self):
        return '<%s entries=%i>' %(self.__class__.__name__, len(self))

class Photo(object):
    zope.interface.implements(interfaces.IPhoto)

    id = fieldproperty.FieldProperty(interfaces.IPhoto['id'])
    owner = fieldproperty.FieldProperty(interfaces.IPhoto['owner'])
    secret = fieldproperty.FieldProperty(interfaces.IPhoto['secret'])
    server = fieldproperty.FieldProperty(interfaces.IPhoto['server'])
    title = fieldproperty.FieldProperty(interfaces.IPhoto['title'])
    ispublic = fieldproperty.FieldProperty(interfaces.IPhoto['ispublic'])
    isfriend = fieldproperty.FieldProperty(interfaces.IPhoto['isfriend'])
    isfamily = fieldproperty.FieldProperty(interfaces.IPhoto['isfamily'])

    def __init__(self, id, owner, secret, server, title,
                 ispublic, isfriend, isfamily):
        self.id = id
        self.owner = owner
        self.secret = secret
        self.server = server
        self.title = title
        self.ispublic = ispublic
        self.isfriend = isfriend
        self.isfamily = isfamily

    @classmethod
    def fromElement(self, element):
        """See interfaces.IBaseFlickrObject"""
        args = dict([
            (name, field.fromUnicode(unicode(element.get(name))))
            for name, field in zope.schema.getFields(interfaces.IPhoto).items()
            ])
        return Photo(**args)

    def __repr__(self):
        return '<%s %i>' %(self.__class__.__name__, self.id)

class APIPhotos(flickr.APIFlickr):
    zope.interface.implements(interfaces.IAPIPhotos)

    def search(self, **kw):
        """See interfaces.IAPIPhotos"""
        args = interfaces.IAPIPhotos['search'].getSignatureInfo()['optional']
        params = dict([(arg, kw.get(arg)) for arg in args
                       if kw.get(arg, None) is not None])
        params = self.initParameters('flickr.photos.search', **params)
        elem = self.execute(params)
        return Photos.fromElement(elem.getchildren()[0])


def search(api_key, **kw):
    __doc__ = interfaces.IAPIPhotos['search'].__doc__

    return APIPhotos(api_key).search(**kw)
