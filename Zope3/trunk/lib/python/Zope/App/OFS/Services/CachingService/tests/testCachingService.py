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

$Id: testCachingService.py,v 1.6 2002/12/12 15:28:17 mgedmin Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Interface.Verify import verifyObject
from Zope.App.Caching.ICache import ICache
from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.OFS.Services.CachingService.CacheConfiguration \
     import CacheConfiguration
from Zope.App.OFS.Services.ConfigurationInterfaces import Active, Registered
from Zope.App.OFS.Services.LocalEventService.tests.EventSetup import EventSetup
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.App.Traversing import getPhysicalPathString, traverse


def sort(list):
    list.sort()
    return list


class CacheStub:

    __implements__ = ICache

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "CacheStub(%r)" % self.name


class CachingServiceSetup(EventSetup):

    def createCachingService(self, path=None):
        from Zope.App.OFS.Services.CachingService.CachingService \
             import CachingService

        folder = self.rootFolder
        if path is not None:
            folder = traverse(folder, path)

        if not folder.hasServiceManager():
            self.createServiceManager(folder)

        default = traverse(folder, '++etc++Services/Packages/default')
        key = default.setObject("myCachingService", CachingService())
        service = traverse(default, key)

        path = getPhysicalPathString(service)
        configuration = ServiceConfiguration("Caching", path)
        configure = traverse(default, 'configure')
        key = configure.setObject(None, configuration)
        traverse(configure, key).status = Active

        return service

    def addCache(self, name, cache=None, cname=None, status=Active, folder=''):
        if not cache: cache = CacheStub("%s/%s" % (folder, name))
        if not cname: cname = name
        default = traverse(self.rootFolder,
                           folder +'/++etc++Services/Packages/default')
        key = default.setObject(cname, cache)
        cache = traverse(default, key)
        configure = traverse(default, 'configure')
        key = configure.setObject(None, CacheConfiguration(name,
                                            getPhysicalPathString(cache)))
        traverse(configure, key).status = status
        return cache


class TestCachingService(CachingServiceSetup, TestCase):

    def setUp(self):
        CachingServiceSetup.setUp(self)
        self.service = self.createCachingService()
        self.cache1 = self.addCache('cache1')
        self.cache2 = self.addCache('cache2')
        self.cache3 = self.addCache('cache3', status=Registered)
        self.service_f1 = self.createCachingService('folder1')
        self.cache1_f1 = self.addCache('cache1', folder='folder1')
        self.cache4_f1 = self.addCache('cache4', folder='folder1')

    def test_interface(self):
        from Zope.App.OFS.Services.CachingService.CachingService \
             import ILocalCachingService
        verifyObject(ILocalCachingService, self.service)
        verifyObject(ICachingService, self.service)

    def test_getCache(self):
        self.assertEqual(self.cache1, self.service.getCache('cache1'))
        self.assertEqual(self.cache2, self.service.getCache('cache2'))
        self.assertRaises(KeyError, self.service.getCache, 'cache3')
        self.assertRaises(KeyError, self.service.getCache, 'cache4')

        self.assertEqual(self.cache1_f1, self.service_f1.getCache('cache1'))
        self.assertEqual(self.cache2, self.service_f1.getCache('cache2'))
        self.assertRaises(KeyError, self.service_f1.getCache, 'cache3')
        self.assertEqual(self.cache4_f1, self.service_f1.getCache('cache4'))
        self.assertRaises(KeyError, self.service_f1.getCache, 'cache5')

    def test_queryCache(self):
        self.assertEqual(self.cache1, self.service.queryCache('cache1'))
        self.assertEqual(self.cache2, self.service.queryCache('cache2'))
        self.assertEqual(None, self.service.queryCache('cache3'))
        self.assertEqual('XX', self.service.queryCache('cache4', 'XX'))
        self.assertEqual(None, self.service.queryCache('cache3'))
        self.assertEqual('YY', self.service.queryCache('cache4', 'YY'))

        self.assertEqual(self.cache1_f1, self.service_f1.queryCache('cache1'))
        self.assertEqual(self.cache2, self.service_f1.queryCache('cache2'))
        self.assertEqual(None, self.service_f1.queryCache('cache3'))
        self.assertEqual('ZZ', self.service_f1.queryCache('cache3', 'ZZ'))
        self.assertEqual(self.cache4_f1, self.service_f1.queryCache('cache4'))
        self.assertEqual(None, self.service_f1.queryCache('cache5'))
        self.assertEqual('12', self.service_f1.queryCache('cache5', '12'))

    def test_getAvailableCaches(self):
        self.assertEqual(['cache1', 'cache2'],
                         sort(self.service.getAvailableCaches()))
        self.assertEqual(['cache1', 'cache2', 'cache4'],
                         sort(self.service_f1.getAvailableCaches()))


def test_suite():
    return TestSuite((
        makeSuite(TestCachingService),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
