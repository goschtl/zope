##############################################################################
#
# Copyright (c) 2004 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Provide basic resource functionality

$Id: browser.py 5259 2004-06-23 15:59:52Z philikon $
"""

from Acquisition import Explicit, aq_inner, aq_parent
from browser import BrowserView
from zope.interface import implements
from zope.component.interfaces import IResource
from zope.component import getViewProviding
from zope.app.traversing.browser.interfaces import IAbsoluteURL
from zope.app.datetimeutils import time as timeFromDateTimeString
from zope.app.publisher.fileresource import File, Image
from zope.app.publisher.pagetemplateresource import PageTemplate

class Resource(Explicit):
    """A publishable resource
    """

    implements(IResource)

    def __init__(self, request):
        self.request = request

    def __call__(self):
        name = self.__name__
        if name.startswith('++resource++'):
            name = name[12:]
        container = aq_parent(self)

        url = str(getViewProviding(container, IAbsoluteURL, self.request))
        return "%s/++resource++%s" % (url, name)


class PageTemplateResource(BrowserView, Resource):

    #implements(IBrowserPublisher)

    def __browser_default__(self, request):
        return self, ()

    def __call__(self):
        pt = self.context
        return pt(self.request)

class FileResource(BrowserView, Resource):
    """A publishable file-based resource"""

    #implements(IBrowserPublisher)

    def __browser_default__(self, request):
        return self, (request.method,)

    def GET(self):
        """Default content"""

        file = self.context
        request = self.request
        response = request.response

        # HTTP If-Modified-Since header handling. This is duplicated
        # from OFS.Image.Image - it really should be consolidated
        # somewhere...
        header = request.getHeader('If-Modified-Since', None)
        if header is not None:
            header = header.split(';')[0]
            # Some proxies seem to send invalid date strings for this
            # header. If the date string is not valid, we ignore it
            # rather than raise an error to be generally consistent
            # with common servers such as Apache (which can usually
            # understand the screwy date string as a lucky side effect
            # of the way they parse it).
            try:    mod_since=long(timeFromDateTimeString(header))
            except: mod_since=None
            if mod_since is not None:
                if getattr(file, 'lmt', None):
                    last_mod = long(file.lmt)
                else:
                    last_mod = long(0)
                if last_mod > 0 and last_mod <= mod_since:
                    response.setStatus(304)
                    return ''

        response.setHeader('Content-Type', file.content_type)
        response.setHeader('Last-Modified', file.lmh)

        # Cache for one day
        response.setHeader('Cache-Control', 'public,max-age=86400')
        f = open(file.path, 'rb')
        data = f.read()
        f.close()

        return data

    def HEAD(self):
        file = self.context
        response = self.request.response
        response = self.request.response
        response.setHeader('Content-Type', file.content_type)
        response.setHeader('Last-Modified', file.lmh)
        # Cache for one day
        response.setHeader('Cache-Control', 'public,max-age=86400')
        return ''

class ResourceFactory:

    factory = None
    resource = None

    def __init__(self, name, path, resource_factory=None):
        self.__name = name
        self.__rsrc = self.factory(path)
        if resource_factory is not None:
            self.resource = resource_factory

    def __call__(self, request):
        resource = self.resource(self.__rsrc, request)
        resource.__name__ = self.__name
        return resource

class PageTemplateResourceFactory(ResourceFactory):
    """A factory for Page Template resources"""

    factory = PageTemplate
    resource = PageTemplateResource

class FileResourceFactory(ResourceFactory):
    """A factory for File resources"""

    factory = File
    resource = FileResource

class ImageResourceFactory(ResourceFactory):
    """A factory for Image resources"""

    factory = Image
    resource = FileResource
