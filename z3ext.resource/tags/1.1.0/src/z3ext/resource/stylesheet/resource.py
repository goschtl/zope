##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
from zope import interface
from zope.component.factory import Factory
from zope.app.component.hooks import getSite

from z3c.zrtresource.replace import Replace
from z3c.zrtresource.processor import ZRTProcessor

from z3ext.resource.fileresource import File, FileResource
from z3ext.resource.interfaces import IResourceFactory, IResourceFactoryType

from packer import CSSPacker

packers = {'full': CSSPacker('full'),
           'save': CSSPacker('save')}


class ZRTFileResource(FileResource):
    """ zrt resource """
    
    _commands_file = ''

    def __init__(self, context, request, media='', compression='', **kw):
        self.context = context
        self.request = request
        self.media = media
        self.compression = compression

    def index_html(self, *args):
        """ make ResourceRegistry happy """
        value = self.GET()
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        return value

    def render(self, request):
        file = self.chooseContext()
        f = open(file.path,'rb')
        data = f.read()
        f.close()
        p = ZRTProcessor(data, commands={'replace': Replace})
        return p.process(getSite(), self.request)

    def GET(self):
        """ default content """
        data = super(ZRTFileResource, self).GET()
        if self.request.response.getStatus() == 304:
            return ''

	# Process the file
        p = ZRTProcessor(data, commands={'replace': Replace})
        result = p.process(getSite(), self.request)

        packer = packers.get(self.compression)
        if packer is not None:
            result = packer.pack(result)

        if self.media:
            result = '@media %s { %s}' % (self.media, result)

        return result


class StylesheetResourceFactory(object):
    interface.implements(IResourceFactory)

    def __init__(self, path, checker, name):
        self.__file = File(path, name)
        self.__checker = checker
        self.__name = name

    def __call__(self, request, **kwargs):
        resource = ZRTFileResource(self.__file, request, **kwargs)
        resource.__Security_checker__ = self.__checker

        resource.__name__ = self.__name
        return resource


stylesheetfactory = Factory(StylesheetResourceFactory)
interface.directlyProvides(stylesheetfactory, IResourceFactoryType)
