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
"""
$Id$
"""
__docformat__ = "reStructuredText"

from zope import component
from zope import interface

from zope.traversing.api import canonicalPath
from zope.publisher.browser import BrowserView
from zope.traversing.browser.absoluteurl import absoluteURL

from lovely.viewcache.interfaces import IViewCache, ICacheableView


class CacheMixinBase(object):
    interface.implements(ICacheableView)

    _cachingOn = True
    __cachedValue__ = None
    _dynamicCachingDeps = ()

    @apply
    def cachingOn():
        def get(self):
            return getattr(super(CacheMixinBase, self),
                           'cachingOn',
                           self._cachingOn)
        def set(self, value):
            self._cachingOn = value
        return property(get, set)

    @property
    def cachingKey(self):
        return getattr(super(CacheMixinBase, self),
                       'cachingKey',
                       self.__name__)

    @property
    def staticCachingDeps(self):
        return getattr(super(CacheMixinBase, self),
                       'staticCachingDeps',
                       self._staticCachingDeps)

    @apply
    def dynamicCachingDeps():
        def get(self):
            return getattr(super(CacheMixinBase, self),
                                 'dynamicCachingDeps',
                                 self._dynamicCachingDeps)
        def set(self, value):
            self._dynamicCachingDeps = value
        return property(get, set)

    def getCache(self):
        return component.queryUtility(IViewCache)

    def _getCachePath(self):
        url = absoluteURL(self, self.request)
        return '/'.join(url.split('/')[3:])

    def _getCachedResult(self):
        self.__cachedValue__ = None
        if self.cachingOn:
            cache = self.getCache()
            if cache is not None:
                result = cache.query(self._getCachePath(),
                                     dict(key=self.cachingKey))
                if result is not None:
                    self.__cachedValue__ = result
        return self.__cachedValue__ is not None

    def _setCachedResult(self, value):
        self.__cachedValue__ = value
        if self.cachingOn:
            cache = self.getCache()
            if cache is not None:
                deps = set(self.staticCachingDeps)
                deps.update(self.dynamicCachingDeps)
                cache.set(value,
                          self._getCachePath(),
                          dict(key=self.cachingKey),
                          lifetime=self.lifetime,
                          dependencies=deps)


class CachedViewMixin(CacheMixinBase):

    def __call__(self, *args, **kwargs):
        if not self._getCachedResult():
            result = super(CacheMixinBase, self).__call__(*args, **kwargs)
            self._setCachedResult(result)
        return self.__cachedValue__


def cachedView(ViewClass, dependencies=(), minAge=0, maxAge=None):
    """A factory to provide a view which is possibly in the view cache."""
    klass = ViewClass
    if ICacheableView not in interface.implementedBy(klass):
        attrs = dict(_staticCachingDeps=dependencies,
                     lifetime = (minAge, maxAge),
                     __name__=None,
                    )
        klass = type('<ViewCache for %s>'% ViewClass.__name__,
                     (CachedViewMixin, ViewClass, ),
                     attrs)
    return klass


class CachedViewletMixin(CacheMixinBase):

    def _getCachePath(self):
        url = absoluteURL(self.__parent__, self.request)
        url = '/'.join(url.split('/')[3:])
        return '%s/%s'% (url,
                         '/'.join([self.__parent__.__name__,
                                   self.manager.__name__,
                                   self.__name__,])
                        )

    def update(self):
        if not self._getCachedResult():
            super(CachedViewletMixin, self).update()

    def render(self):
        if self.__cachedValue__ is None:
            if not self._getCachedResult():
                result = super(CachedViewletMixin, self).render()
                self._setCachedResult(result)
        return self.__cachedValue__


def cachedViewlet(ViewClass, dependencies=(), minAge=0, maxAge=None):
    """A factory to provide a viewlet which is possibly in the view cache."""
    klass = ViewClass
    if ICacheableView not in interface.implementedBy(klass):
        # our class is not cached, so make it a cached class
        attrs = dict(_staticCachingDeps=dependencies,
                     lifetime = (minAge, maxAge),
                     __name__=None,
                    )
        klass = type('<ViewletCache for %s>'% ViewClass.__name__,
                     (CachedViewletMixin, ViewClass, ),
                     attrs)
    return klass

