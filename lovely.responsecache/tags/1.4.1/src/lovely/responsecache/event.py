##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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
__docformat__ = "reStructuredText"

from zope.app.publication.interfaces import IEndRequestEvent
from zope import component
from zope.app.publication.interfaces import IBeforeTraverseEvent
from interfaces import IResponseCacheSettings, IPurge
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.contentprovider.interfaces import IBeforeUpdateEvent
from zope.contentprovider.interfaces import IContentProvider
from zope.publisher.interfaces.browser import IBrowserRequest
from types import UnicodeType
from zope.publisher.http import getCharsetUsingRequest
from zope.security.proxy import removeSecurityProxy

class RenderWrapper(object):

    def __init__(self, provider, settings, request):
        self.render = provider.render
        self.settings = settings
        self.provider = provider
        self.request = request

    def __call__(self):
        cached = getattr(self.provider, '_UpdateWrapper__cached_result', None)
        encoding = getCharsetUsingRequest(self.request) or 'utf-8'
        if cached is not None:
            return cached.decode(encoding)
        res = body = self.render()
        if type(body) is UnicodeType:
            encoding = getCharsetUsingRequest(self.request) or 'utf-8'
            body = body.encode(encoding)

        self.settings.cache.set(body, self.settings.key,
                                dependencies=self.settings.dependencies,
                                lifetime=self.settings.lifetime,
                                raw=True)

        return res


class UpdateWrapper(object):

    def __init__(self, provider, settings, request):
        self.provider = provider
        self.update = provider.update
        self.settings = settings
        self.request = request

    def __call__(self):
        cached = self.settings.cache.query(self.settings.key, raw=True)
        if cached:
            hit = self.request.response.getHeader('X-Memcached-Hit')
            if hit:
                hit += ' %s' % self.settings.key
            else:
                hit = self.settings.key
            self.request.response.setHeader('X-Memcached-Hit', hit)
            self.provider.__cached_result = cached
            return
        miss = self.request.response.getHeader('X-Memcached-Miss')
        if miss:
            miss += ' %s' % self.settings.key
        else:
            miss = self.settings.key
        self.request.response.setHeader('X-Memcached-Miss', miss)
        return self.update()


@component.adapter(IContentProvider, IBeforeUpdateEvent)
def setCache(provider, ev):
    settings = component.queryMultiAdapter(
        (provider, ev.request), IResponseCacheSettings)
    if settings is None or settings.cache is None:
        return
    provider = removeSecurityProxy(provider)
    provider.update = UpdateWrapper(provider, settings, ev.request)
    provider.render = RenderWrapper(provider, settings, ev.request)

@component.adapter(IEndRequestEvent)
def setAuthInfoCookie(ev):
    """sets a cookie that tells if the user authenticated or not.
    This is not used for authentication. This is just usefull for
    frontend caching servers to rewrite urls for caching."""
    if IBrowserRequest.providedBy(ev.request):
        if ev.request.principal is None:
            auth = False
        else:
            auth = not IUnauthenticatedPrincipal.providedBy(ev.request.principal)
        ev.request.response.setCookie(
                'z3.authenticated',
                str(auth),
                path = '/',
                expires = '"Tue, 19 Jan 2038 00:00:00 GMT"')

