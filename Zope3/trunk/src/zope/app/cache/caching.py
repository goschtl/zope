##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Helpers for caching."""

from zope.component import getAdapter, getService, ComponentLookupError
from zope.app.interfaces.cache.cache import ICacheable
from zope.app.interfaces.traversing import IPhysicallyLocatable


def getCacheForObj(obj):
    """Returns the cache associated with obj or None."""
    adapter = getAdapter(obj, ICacheable)
    cache_id = adapter.getCacheId()
    if not cache_id:
        return None
    service = getService(obj, "Caching")
    return service.getCache(cache_id)

def getLocationForCache(obj):
    """Returns the location to be used for caching the object or None."""
    try:
        locatable = getAdapter(obj, IPhysicallyLocatable)
        return "/".join(locatable.getPhysicalPath())
    except (ComponentLookupError, TypeError):
        return None
