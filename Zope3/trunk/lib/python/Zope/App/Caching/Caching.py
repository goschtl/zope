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

from Zope.ComponentArchitecture import getAdapter, getService
from Zope.App.Caching.ICacheable import ICacheable

def getCacheForObj(obj):
    """Returns the cache associated with obj or None."""
    adapter = getAdapter(obj, ICacheable)
    cache_id = adapter.getCacheId()
    if not cache_id:
        return None
    service = getService(obj, "Caching")
    return service.getCache(cache_id)

