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

$Id: test_caching.py,v 1.12 2004/02/25 23:02:22 faassen Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests import ztapi
from zope.app.interfaces.cache import ICacheable, ICachingService
from zope.app.cache.caching import getCacheForObj
from zope.app.cache.annotationcacheable import AnnotationCacheable
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.attributeannotations import AttributeAnnotations
from zope.component import getAdapter
from zope.component import getService
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.service import serviceManager as sm
from zope.app.interfaces.services.service import ISimpleService
from zope.interface import implements

class ObjectStub:
    implements(IAttributeAnnotatable)

class CacheStub:
    pass

class CachingServiceStub:

    implements(ICachingService, ISimpleService)

    def __init__(self):
        self.caches = {}

    def getCache(self, name):
        return self.caches[name]

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        super(Test, self).setUp()
        ztapi.provideAdapter(
            IAttributeAnnotatable, IAnnotations,
            AttributeAnnotations)
        ztapi.provideAdapter(
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
