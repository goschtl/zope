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
"""This module implements the flickr.blogs namespace

http://www.flickr.com/services/api/

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface
from zope.schema import fieldproperty
from lovely.flickr import interfaces, flickr


class Blogs(list):
    zope.interface.implements(interfaces.IBlogs)

    @classmethod
    def fromElement(self, element):
        """See interfaces.IBaseFlickrObject"""
        blogs = Blogs()
        for child in element.getchildren():
            blogs.append(Blog.fromElement(child))
        return blogs


class Blog(object):
    zope.interface.implements(interfaces.IBlog)

    id = fieldproperty.FieldProperty(interfaces.IBlog['id'])
    name = fieldproperty.FieldProperty(interfaces.IBlog['name'])
    needspassword = fieldproperty.FieldProperty(
        interfaces.IBlog['needspassword'])
    url = fieldproperty.FieldProperty(interfaces.IBlog['url'])

    def __init__(self, id, name, needspassword, url):
        self.id = id
        self.name = name
        self.needspassword = needspassword
        self.url = url

    @classmethod
    def fromElement(self, element):
        """See interfaces.IBaseFlickrObject"""
        args = dict([
            (name, field.fromUnicode(unicode(element.get(name))))
            for name, field in zope.schema.getFields(interfaces.IBlog).items()
            ])
        return Blog(**args)

    def __repr__(self):
        return '<%s %i - %r>' %(self.__class__.__name__, self.id, self.name)


class APIBlogs(flickr.APIFlickr):
    """This class provides a pythonic interface to the ``flickr.blogs``
       namespace.
    """
    zope.interface.implements(interfaces.IAPIBlogs)

    def getList(self):
        """See interfaces.IAPIBlogs"""
        params = self.initParameters('flickr.blogs.getList')
        self.addAuthToken(params)
        self.sign(params)
        elem = self.execute(params)
        return Blogs.fromElement(elem.getchildren()[0])

    def postPhoto(self, blog_id, photo_id, title, description,
                  blog_password=None):
        """See interfaces.IAPIBlogs"""
        params = self.initParameters(
            'flickr.blogs.postPhoto', blog_id=blog_id, photo_id=photo_id,
            title=title, description=description)
        if blog_password is not None:
            params['blog_password'] = blog_password
        self.addAuthToken(params)
        self.sign(params)
        self.execute(params, 'POST')

def getList(api_key, secret, auth_token):
    __doc__ = interfaces.IAPIBlogs['getList'].__doc__
    return APIBlogs(api_key, secret, auth_token).getList()

def postPhoto(api_key, secret, auth_token, *args, **kw):
    __doc__ = interfaces.IAPIBlogs['postPhoto'].__doc__
    return APIBlogs(api_key, secret, auth_token).postPhoto(*args, **kw)
