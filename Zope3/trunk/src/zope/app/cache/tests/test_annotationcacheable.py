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

$Id$
"""
import unittest
from zope.interface import implements

from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.annotation.interfaces import IAnnotations, IAttributeAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.cache.annotationcacheable import AnnotationCacheable
from zope.app.cache.interfaces import ICache

class ObjectStub:
    implements(IAttributeAnnotatable)


class CacheStub:
    implements(ICache)
    def __init__(self):
        self.invalidated = []

    def invalidate(self, obj):
        self.invalidated.append(obj)


class TestAnnotationCacheable(PlacelessSetup, unittest.TestCase):
    def setUp(self):
        super(TestAnnotationCacheable, self).setUp()
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)

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
        cache1 = CacheStub()
        ztapi.provideUtility(ICache, cache1, "cache1")
        cache2 = CacheStub()
        ztapi.provideUtility(ICache, cache2, "cache2")
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
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestAnnotationCacheable))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
