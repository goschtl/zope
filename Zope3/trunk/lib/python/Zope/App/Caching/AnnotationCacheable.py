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
"""An adapter of annotatable objects."""

from Zope.ComponentArchitecture import getAdapter, getService
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.Caching.ICacheable import ICacheable

annotation_key = 'Zope.App.Caching.CacheManager'

class AnnotationCacheable:
    """Stores cache information in object's annotations."""

    __implements__ = ICacheable

    def __init__(self, context):
        self._context = context

    def getCacheId(self):
        """See Zope.App.Caching.ICacheable"""
        annotations = getAdapter(self._context, IAnnotations)
        return annotations.get(annotation_key, None)

    def setCacheId(self, id):
        """See Zope.App.Caching.ICacheable"""
        # Remove object from old cache
        old_cache_id = self.getCacheId()
        if old_cache_id and old_cache_id != id:
            service = getService(self._context, "Caching")
            cache = service.getCache(old_cache_id)
            cache.invalidate(self._context)
        annotations = getAdapter(self._context, IAnnotations)
        annotations[annotation_key] = id

    cacheId = property(getCacheId, setCacheId, None, "Associated cache name")
