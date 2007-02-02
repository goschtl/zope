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

from zope import interface
from zope import component

from zope.traversing.api import canonicalPath
from zope.location.interfaces import ILocation
from zope.viewlet.viewlet import ViewletBase
from zope.viewlet.manager import ViewletManagerBase
from zope.viewlet.interfaces import IViewlet

from lovely.viewcache.interfaces import (ICachedViewletManager,
                                         ICacheableView,
                                         IViewCache,
                                        )


class CachedViewletManager(ViewletManagerBase):
    interface.implements(ICachedViewletManager)

    __name__ = u''

    def getCache(self):
        return component.queryUtility(IViewCache)

    def _getCachePath(self, viewlet):
        return u'%s/%s/%s'% (canonicalPath(self.context),
                            unicode(self.__name__),
                            unicode(viewlet.__name__))

    def _updateViewlets(self):
        cache = self.getCache()
        if cache is not None:
            viewlets = []
            for viewlet in self.viewlets:
                # try to get the cached value from the cache
                if ICacheableView.providedBy(viewlet) and viewlet.cachingOn:
                    result = cache.query(self._getCachePath(viewlet),
                                         dict(key=viewlet.key))
                    if result is not None:
                        viewlet.__cachedValue__ = result
                viewlets.append(viewlet)
            self.viewlets = viewlets
        for viewlet in self.viewlets:
            if not hasattr(viewlet, '__cachedValue__'):
                viewlet.update()

    def render(self):
        cache = self.getCache()
        result = []
        for viewlet in self.viewlets:
            if not hasattr(viewlet, '__cachedValue__'):
                viewletResult = viewlet.render()
                if (    cache is not None
                    and ICacheableView.providedBy(viewlet)
                    and viewlet.cachingOn
                   ):
                    deps = set(viewlet.staticCachingDeps)
                    deps.update(viewlet.dynamicCachingDeps)
                    cache.set(viewletResult,
                              self._getCachePath(viewlet),
                              dict(key=viewlet.key),
                              dependencies=deps)
                result.append(viewletResult)
            else:
                result.append(viewlet.__cachedValue__)
        return u'\n'.join([r for r in result])

