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

$Id: test_annotationcacheable.py,v 1.7 2003/03/11 16:10:56 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getService
from zope.app.services.servicenames import Adapters
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.cache.annotationcacheable import AnnotationCacheable
from zope.app.interfaces.cache.cache import ICachingService
from zope.component.service import serviceManager as sm
from zope.app.interfaces.services.service import ISimpleService

class ObjectStub:
    __implements__ = IAttributeAnnotatable


class CacheStub:
    def __init__(self):
        self.invalidated = []

    def invalidate(self, obj):
        self.invalidated.append(obj)


class CachingServiceStub:
    __implements__ = ICachingService, ISimpleService

    def __init__(self):
        self.caches = {}

    def getCache(self, name):
        return self.caches[name]


class TestAnnotationCacheable(PlacelessSetup, TestCase):
    def setUp(self):
        PlacelessSetup.setUp(self)
        getService(None, Adapters).provideAdapter(
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
        # Test that setting a different cache ID invalidates the old cached
        # value
        self.service.caches['cache1'] = cache1 = CacheStub()
        self.service.caches['cache2'] = cache2 = CacheStub()
        ob = ObjectStub()
        adapter = AnnotationCacheable(ob)
        adapter.setCacheId('cache1')
        self.assertEquals(cache1.invalidated, [],
                          "called invalidate too early")
        adapter.setCacheId('cache2')
        self.assertEquals(cache1.invalidated, [ob], "did not call invalidate")
        adapter.setCacheId('cache2')
        self.assertEquals(
            cache2.invalidated, [],
            "called invalidate when reassigning to the same cache")


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestAnnotationCacheable))
    return suite


if __name__ == '__main__':
    main(defaultTest='test_suite')
