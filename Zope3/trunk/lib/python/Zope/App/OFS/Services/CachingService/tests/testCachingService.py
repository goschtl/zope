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
"""CachingService tests.

$Id: testCachingService.py,v 1.3 2002/12/06 11:01:11 alga Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalServiceManager import \
     serviceManager as sm
from Interface.Verify import verifyClass, verifyObject

from Zope.App.Caching.ICache import ICache
from Zope.App.Caching.ICachingService import ICachingService

def sort(list):
    list.sort()
    return list

class CacheStub:

    __implements__ = ICache

class TestCachingService(PlacelessSetup, TestCase):

    def setUp(self):
        from Zope.App.OFS.Services.CachingService.CachingService \
             import CachingService
        PlacelessSetup.setUp(self)
        self.cache1 = CacheStub()
        self.cache2 = CacheStub()
        self.service = CachingService()
        self.service.setObject('cache1', self.cache1)
        self.service.setObject('cache2', self.cache2)
        sm.defineService('Caching', ICachingService)
        sm.provideService('Caching', self.service)

    def test_interface(self):
        from Zope.App.OFS.Services.CachingService.CachingService \
             import ILocalCachingService
        verifyObject(ILocalCachingService, self.service)
        verifyObject(ICachingService, self.service)

    def testGetCache(self):
        self.assertEqual(self.cache1,
                         self.service.getCache('cache1'))
        self.assertRaises(KeyError, self.service.getCache, 'cache3')

    def testQueryCache(self):
        self.assertEqual(self.cache1,
                         self.service.queryCache('cache1'))
        self.assertEqual(None,
                         self.service.queryCache('cache3'))
        self.assertEqual('Error',
                         self.service.queryCache('cache3', 'Error'))

    def testGetAvailableCaches(self):
        self.assertEqual(['cache1', 'cache2'],
                         sort(self.service.getAvailableCaches()))

    def testIsAddable(self):
        self.assertEqual(1, self.service.isAddable(ICache))
        self.assertEqual(0, self.service.isAddable(ICachingService))


def test_suite():
    return TestSuite((
        makeSuite(TestCachingService),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
