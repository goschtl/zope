##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite
from zope.traversing.browser.interfaces import IAbsoluteURL

from packer import CSSPacker
from resource import Resource
from package import Package, PackageFactory

packers = {'full': CSSPacker('full'),
           'save': CSSPacker('save')}


class Stylesheet(Resource):

    def __init__(self, path, name='', media='all', rel='stylesheet', compression='full'):
        super(Stylesheet, self).__init__(path)

        self.rel = rel
        self.media = media
        self.compression = compression
        self.resource_path = '++resource++/%s'%path

    def render(self, request, compress=True):
        content = super(Stylesheet, self).render(request, compress=True)

        if compress:
            packer = packers.get(self.compression, None)
            if packer is not None:
                content = packer.pack(content)

        url = '%s/%s'%(
	    str(getMultiAdapter((getSite(), request), IAbsoluteURL)), self.resource_path)
        content = ' /* %s */\n%s'%(url, content)

        if self.media:
            content = '@media %s { %s}' % (self.media, content)

        return content


class StylesheetPackage(Package):
    type = u'stylesheet'
    content_type = u'text/css'

    def link(self):
        return '<link rel="stylesheet" type="text/css" media="screen" href="%s" />'%self()

    def addResource(self, path, **kw):
        self.resources.append(Stylesheet(path, **kw))


packageFactory = PackageFactory(StylesheetPackage)
