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

$Id: testCaching.py,v 1.1 2002/10/03 10:37:50 mgedmin Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Caching.ICacheable import ICacheable
from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.Caching.Caching import getCacheForObj
from Zope.App.Caching.AnnotationCacheable import AnnotationCacheable
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations
from Zope.ComponentArchitecture import getAdapter
from Zope.ComponentArchitecture import getService
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalServiceManager import \
     serviceManager as sm

class ObjectStub:
    __implements__ = IAttributeAnnotatable

class CacheStub:
    pass

class CachingServiceStub:

    __implements__ = ICachingService

    def __init__(self):
        self.caches = {}

    def getCache(self, name):
        return self.caches[name]

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        getService(None, "Adapters").provideAdapter(
            IAttributeAnnotatable, IAnnotations,
            AttributeAnnotations)
        getService(None, "Adapters").provideAdapter(
            IAnnotatable, ICacheable,
            AnnotationCacheable)
        self.service = CachingServiceStub()
        sm.defineService('Caching', ICachingService)
        sm.provideService('Caching', self.service)

    def testGetCacheForObj(self):
        self.service.caches['my_cache'] = my_cache = CacheStub()

        obj = ObjectStub()
        self.assertEquals(getCacheForObj(obj), None)

        getAdapter(obj, ICacheable).setCacheId("my_cache")

        self.assertEquals(getCacheForObj(obj), my_cache)


def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
