##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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

import time

import zope.component

from zope.viewlet import viewlet

from zope.app.publisher.browser.fileresource import FileResource
from zope.app.form.browser.widget import renderElement

from interfaces import ICollectorUtility


class CollectorResource(FileResource):

    def __init__(self, request):
        self.request = request

    def GET(self):
        rs = zope.component.getUtility(ICollectorUtility, self.__name__)

        resources = rs.getResources(self.request)
        if rs.content_type is not None:
            self.request.response.setHeader('Content-Type', rs.content_type)
        secs = 31536000
        self.request.response.setHeader('Cache-Control',
                                        'public,max-age=%s' % secs)
        t = time.time() + secs
        self.request.response.setHeader('Expires',
                       time.strftime("%a, %d %b %Y %H:%M:%S GMT",
                                     time.gmtime(t)))
        return resources


class CollectorViewlet(viewlet.ViewletBase):

    @property
    def collector(self):
        return self.__name__

    def renderElement(self, url):
        return self.template% {'url':url}

    def render(self):
        originalHeader = self.request.response.getHeader('Content-Type')
        if originalHeader is None:
            originalHeader = "text/html"
        rs = zope.component.getUtility(ICollectorUtility, self.collector)
        versionedresource = rs.getUrl(self.context,self.request)
        view=zope.component.getAdapter(self.request, name=self.collector)
        url = '%s?hash=%s'% (view(), versionedresource)
        script = self.renderElement(url)
        self.request.response.setHeader('Content-Type', originalHeader)
        return script


class JSCollectorViewlet(CollectorViewlet):
    """Render a link to include Javascript resources"""

    def renderElement(self, url):
        return renderElement('script',
                             src=url,
                             extra='type="text/javascript"',
                             contents=' ',
                             )


class CSSCollectorViewlet(CollectorViewlet):
    """Render a link to include CSS resources"""

    media = 'screen'

    def renderElement(self, url):
        return renderElement('link',
                             rel='stylesheet',
                             href=url,
                             media=self.media,
                             extra='type="text/css"',
                             )


class CSSIE6CollectorViewlet(CollectorViewlet):
    """Renders a IE 7 Only include CSS resource"""

    def renderElement(self, url):
        return '<!--[if lt IE 6]><link rel="stylesheet"'\
               ' type="text/css" href="%s" /><![endif]-->' % url

class CSSIE7CollectorViewlet(CollectorViewlet):
    """Renders a IE 7 Only include CSS resource"""

    def renderElement(self, url):
        return '<!--[if lt IE 7]><link rel="stylesheet"'\
               ' type="text/css" href="%s" /><![endif]-->' % url
