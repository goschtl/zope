##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Versioned Resources Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import zope.component
import zope.interface
import zope.site.hooks
import zope.traversing.browser.absoluteurl
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.publisher.browser import resource, resources
from zope.app.publisher.browser import directoryresource
from zope.app.publisher.browser import fileresource
from zope.app.publisher.browser import pagetemplateresource
from zope.traversing.browser.interfaces import IAbsoluteURL
from z3c.versionedresource import interfaces

class Resources(resources.Resources):

    def publishTraverse(self, request, name):
        '''See interface IBrowserPublisher'''
        try:
            return super(Resources, self).publishTraverse(request, name)
        except NotFound:
            pass

        vm = zope.component.queryUtility(interfaces.IVersionManager)
        if vm is None or vm.version != name:
            raise NotFound(self, name)

        res = resources.Resources(self.context, self.request)
        res.__name__ = vm.version
        return res


class AbsoluteURL(zope.traversing.browser.absoluteurl.AbsoluteURL):
    zope.interface.implementsOnly(IAbsoluteURL)
    zope.component.adapts(interfaces.IVersionedResource, IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __str__(self):
        name = self.context.__name__
        if name.startswith('++resource++'):
            name = name[12:]

        site = zope.site.hooks.getSite()
        base = zope.component.queryMultiAdapter(
            (site, self.request), IAbsoluteURL, name="resource")
        if base is None:
            url = str(zope.component.getMultiAdapter(
                (site, self.request), IAbsoluteURL))
        else:
            url = str(base)

        vm = zope.component.queryUtility(interfaces.IVersionManager)

        return '%s/@@/%s/%s' % (url, vm.version, name)


class Resource(resource.Resource):
    zope.interface.implements(interfaces.IVersionedResource)

class FileResource(fileresource.FileResource):
    zope.interface.implements(interfaces.IVersionedResource)

    # 10 years expiration date
    cacheTimeout = 10 * 365 * 24 * 3600

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.context.path)

class FileResourceFactory(fileresource.FileResourceFactory):
    resourceClass = FileResource

class ImageResourceFactory(fileresource.ImageResourceFactory):
    resourceClass = FileResource


class DirectoryResource(directoryresource.DirectoryResource):
    zope.interface.implements(interfaces.IVersionedResource)

    resource_factories = {
        '.gif':  ImageResourceFactory,
        '.png':  ImageResourceFactory,
        '.jpg':  ImageResourceFactory,
        '.pt':   pagetemplateresource.PageTemplateResourceFactory,
        '.zpt':  pagetemplateresource.PageTemplateResourceFactory,
        }

    default_factory = FileResourceFactory
    directory_factory = None

    def __repr__(self):
        return '<%s %r>' %(self.__class__.__name__, self.context.path)

class DirectoryResourceFactory(directoryresource.DirectoryResourceFactory):
    factoryClass = DirectoryResource

DirectoryResource.directory_factory = DirectoryResourceFactory
