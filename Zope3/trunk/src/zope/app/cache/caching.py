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
"""Helpers for caching.

$Id: caching.py,v 1.8 2004/03/06 16:50:16 jim Exp $
"""
from zope.app import zapi
from zope.app.cache.interfaces import ICacheable
from zope.app.services.servicenames import Caching
from zope.component import ComponentLookupError

def getCacheForObj(obj):
    """Returns the cache associated with obj or None."""
    adapter = ICacheable(obj)
    cache_id = adapter.getCacheId()
    if not cache_id:
        return None
    service = zapi.getService(obj, Caching)
    return service.getCache(cache_id)

def getLocationForCache(obj):
    """Returns the location to be used for caching the object or None."""
    try:
        return zapi.getPath(obj)
    except (ComponentLookupError, TypeError):
        return None
