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
"""Unit test for AnnotationCacheable adapter.

$Id: testAnnotationCacheable.py,v 1.4 2002/10/09 13:08:44 alga Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getService
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations
from Zope.App.Caching.AnnotationCacheable import AnnotationCacheable
from Zope.App.Caching.ICachingService import ICachingService
from Zope.ComponentArchitecture.GlobalServiceManager import \
     serviceManager as sm

class ObjectStub:
    __implements__ = IAttributeAnnotatable

class CacheStub:

    def __init__(self):
        self.invalidated = []

    def invalidate(self, obj):
        self.invalidated.append(obj)

class CachingServiceStub:

    __implements__ = ICachingService

    def __init__(self):
        self.caches = {}

    def getCache(self, name):
        return self.caches[name]

class TestAnnotationCacheable(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        getService(None, "Adapters").provideAdapter(
            IAttributeAnnotatable, IAnnotations,
            AttributeAnnotations)
        self.service = CachingServiceStub()
        sm.defineService('Caching', ICachingService)
        sm.provideService('Caching', self.service)

    def testNormal(self):
        ob = ObjectStub()
        adapter = AnnotationCacheable(ob)
        self.assertEquals(adapter.getCacheId(), None,
                          "initially cache ID should be None")

        adapter.setCacheId("my_id")
        self.assertEquals(adapter.getCacheId(), "my_id",
                          "failed to set cache ID")

    def testInvalidate(self):
        """Test that setting a different cache ID invalidates the old
        cached value"""
        self.service.caches['cache1'] = cache1 = CacheStub()
        self.service.caches['cache2'] = cache2 = CacheStub()
        ob = ObjectStub()
        adapter = AnnotationCacheable(ob)
        adapter.setCacheId('cache1')
        self.assertEquals(cache1.invalidated, [], "called invalidate too early")
        adapter.setCacheId('cache2')
        self.assertEquals(cache1.invalidated, [ob], "did not call invalidate")
        adapter.setCacheId('cache2')
        self.assertEquals(cache2.invalidated, [],
                          "called invalidate when reassigning to the same cache")
                

def test_suite():
    return TestSuite((
        makeSuite(TestAnnotationCacheable),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
