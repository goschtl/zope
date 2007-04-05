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
__docformat__ = 'restructuredtext'

from zope import interface
from zope import schema

from zope.app.cache.interfaces.ram import IRAMCache
from zope.location.interfaces import ILocation

from lovely.viewcache.i18n import _


class ICacheableView(ILocation):
    """A view implements this interface if it is turned into a cachable view"""

    cachingKey = schema.TextLine(
            title = u'Cache key',
            description = u"""
                The key for the specific viewlet in the cache.
                None if the viewlet needs no discrimination.
                Make sure the value is hashable.
                """,
            default = None,
            )

    cachingOn = schema.Bool(
            title = u'Caching on',
            description = u"""
                The view is not cached if this property is False.
                """,
            default=True
            )

    staticCachingDeps = interface.Attribute(
            "Objects the view depends on",
            """Usually this is used to define dependencies on class level.
               This attribute is read only in the CachedView implementation.
            """)

    dynamicCachingDeps = interface.Attribute(
            "Objects the view depends on",
            """"
                This is used for the dynamic dependencies created by the view
                at runtime.
            """)

    def getCachePath():
        """Provide the main key for the cache entry.

        Usually uses the URL without the domain as path.
        Can be overridden if a view wants to provide a path independent of the
        URL.
        """

    def cacheHit(self, *args, **kwargs):
        """Called from __call__ if the result is taken from the cache

        This gives a view a hook to do things which must be done even if the
        cached value is used.
        Example :
            If your view needs a resource using "zc.resourcelibrary" you do
            this here.
        IMPORTANT :
            it is not called if the regular __call__ of the view is used to
            get the result.
        """


class ICacheableViewlet(ICacheableView):
    """A viewlet implements this interface if it is turned into a cachable
       viewlet
    """


class IViewCache(IRAMCache):
    """A special cache used for the view cache."""

    def set(data, ob, key=None, dependencies=None):
        """It is possible to provide dependencies for the cache entry."""

    def invalidate(ob=None, key=None, dependencies=None):
        """Invalidation also allows to invalidate on the dependencies of a
           view.
        """

    def getExtendedStatistics():
        """return an extended statistics dictionary"""


class IZODBViewCache(IViewCache):
    """A cache which stores it's values in the ZODB using a mountpoint."""

    dbName = schema.Choice(
            title=_(u'Database Name'),
            description=_(u"The database to be used for the cache"),
            vocabulary='Database Names',
            )


class IViewModule(interface.Interface):

    def cachedView(viewClass, dependencies=(), minAge=0, maxAge=None):
        """Create a cached view class from an existing view class.

        Returns a class which is using the cache. Caching is done when calling
        the view.

        viewClass : the class which should be turned into a cached class
        dependencies : used for the 'staticCachingDeps'
        minAge : the minimum lifetime of a cache entry for this view. If a
                 view is ivalidated before this time it is marked as
                 invalidated and removed after this time from the cache.
        maxAge : allows to overwrite the maxAge of cache entries in the cache
                 the view is cached. This parameter can not extend the maxAge
                 defined in the cache!
        """

    def cachedViewlet(viewletClass, dependencies=(), minAge=0, maxAge=None):
        """Create a cached view class from an existing view class.

        This is exactly the same an 'cachedView' but allows caching for
        viewlets.

        If a cached value is present 'update' and 'render' is not called
        instead the cached value is returned when calling render. The new
        class is derived from the cachedView class so that it also provides
        caching when the viewlet is called.
        """

