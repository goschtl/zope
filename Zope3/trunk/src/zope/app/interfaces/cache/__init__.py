##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interfaces for cache manager.

$Id: __init__.py,v 1.3 2003/08/19 17:34:17 srichter Exp $
"""
from zope.app import zapi
from zope.app.interfaces.event import ISubscriber
from zope.app.services.servicenames import Caching
from zope.context import ContextProperty
from zope.interface import Interface
from zope.schema import TextLine

class CacheName(TextLine):
    """Cache Name"""

    def __allowed(self):
        """Note that this method works only if the Field is context wrapped.
        """
        service = zapi.queryService(self.context, Caching)
        if service is None:
            return ['']
        else:
            return [''] + list(service.getAvailableCaches())

    allowed_values = ContextProperty(__allowed)


class ICacheable(Interface):
    """Object that can be associated with a cache manager."""

    cacheId = CacheName(
        title=u"Cache Name",
        description=u"The name of the cache used for this object.",
        required=True)

    def getCacheId():
        """Gets the associated cache manager ID."""

    def setCacheId(id):
        """Sets the associated cache manager ID."""


class ICachingService(Interface):

    def getCache(name):
        """Returns a cache object by name."""

    def queryCache(name, default):
        """Return a cache object by name or default."""

    def getAvailableCaches():
        """Returns a list of names of cache objects known to this caching
        service."""


class ICache(ISubscriber):
    """Interface for caches."""

    def invalidate(ob, key=None):
        """Invalidates cached entries that apply to the given object.

        ob is an object location.  If key is specified, only
        invalidates entry for the given key.  Otherwise invalidates
        all entries for the object.
        """

    def invalidateAll():
        """Invalidates all cached entries."""

    def query(ob, key=None, default=None):
        """Returns the cached data previously stored by set().

        ob is the location of the content object being cached.  key is
        a mapping of keywords and values which should all be used to
        select a cache entry.
        """

    def set(data, ob, key=None):
        """Stores the result of executing an operation."""
