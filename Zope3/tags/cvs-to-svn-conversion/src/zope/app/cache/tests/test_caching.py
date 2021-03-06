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
"""Unit tests for caching helpers.

$Id: test_caching.py,v 1.16 2004/03/13 23:00:46 srichter Exp $
"""
import unittest
from zope.interface import implements

from zope.app.tests import ztapi, setup
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.cache.interfaces import ICacheable, ICache
from zope.app.cache.caching import getCacheForObject
from zope.app.cache.annotationcacheable import AnnotationCacheable

class ObjectStub:
    implements(IAttributeAnnotatable)

class CacheStub:
    implements(ICache)

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)
        ztapi.provideAdapter(IAnnotatable, ICacheable,
                             AnnotationCacheable)
        self._cache = CacheStub()
        ztapi.provideUtility(ICache, self._cache, "my_cache")

    def testGetCacheForObj(self):
        obj = ObjectStub()
        self.assertEquals(getCacheForObject(obj), None)
        ICacheable(obj).setCacheId("my_cache")
        self.assertEquals(getCacheForObject(obj), self._cache)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
