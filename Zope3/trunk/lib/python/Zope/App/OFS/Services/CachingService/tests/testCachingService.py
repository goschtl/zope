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

$Id: testCachingService.py,v 1.5 2002/12/11 09:04:08 mgedmin Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Interface.Verify import verifyClass, verifyObject
from Zope.App.Caching.ICache import ICache
from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.OFS.Services.ConfigurationInterfaces import Active
from Zope.App.OFS.Services.LocalEventService.tests.EventSetup import EventSetup
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.App.Traversing import getPhysicalPathString, traverse
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getServiceManager, getService
from Zope.ComponentArchitecture.GlobalServiceManager \
     import serviceManager as sm
from Zope.Event.IObjectEvent import IObjectModifiedEvent


def sort(list):
    list.sort()
    return list


class CacheStub:

    __implements__ = ICache


class CachingServiceSetup(EventSetup):

    def setUp(self):
        EventSetup.setUp(self)

        global_service_manager = getServiceManager(None)
        global_service_manager.defineService("CachingService", ICachingService)
        self.createCachingService()

    def createCachingService(self, path=None):
        from Zope.App.OFS.Services.CachingService.CachingService \
             import CachingService

        folder = self.rootFolder
        if path is not None:
            folder = traverse(folder, path)

        if not folder.hasServiceManager():
            self.createServiceManager(folder)

        sm = traverse(folder, '++etc++Services')
        default = traverse(sm, 'Packages/default')
        default.setObject("myCachingService", CachingService())

        path = "%s/Packages/default/myCachingService" % getPhysicalPathString(sm)
        configuration = ServiceConfiguration("CachingService", path)

        configure = traverse(default, 'configure')
        configure = traverse(default, 'configure')
        key = configure.setObject("myCachingServiceDir", configuration)
        traverse(configure, key).status = Active


class TestCachingService(CachingServiceSetup, TestCase):

    def setUp(self):
        CachingServiceSetup.setUp(self)
        self.cache1 = CacheStub()
        self.cache2 = CacheStub()
        self.service = getService(self.rootFolder, "CachingService")
        self.service.setObject('cache1', self.cache1)
        self.service.setObject('cache2', self.cache2)

    def test_interface(self):
        from Zope.App.OFS.Services.CachingService.CachingService \
             import ILocalCachingService
        verifyObject(ILocalCachingService, self.service)
        verifyObject(ICachingService, self.service)

    def test_getCache(self):
        self.assertEqual(self.cache1,
                         self.service.getCache('cache1'))
        self.assertRaises(KeyError, self.service.getCache, 'cache3')

    def test_queryCache(self):
        self.assertEqual(self.cache1,
                         self.service.queryCache('cache1'))
        self.assertEqual(None,
                         self.service.queryCache('cache3'))
        self.assertEqual('Error',
                         self.service.queryCache('cache3', 'Error'))

    def test_getAvailableCaches(self):
        self.assertEqual(['cache1', 'cache2'],
                         sort(self.service.getAvailableCaches()))

    def test_isAddable(self):
        self.assertEqual(1, self.service.isAddable(ICache))
        self.assertEqual(0, self.service.isAddable(ICachingService))

    def test_setObject(self):
        # setObject called in setUp... Ugh...
        self.assertEqual(self.service.listSubscriptions(self.cache1),
                         [(IObjectModifiedEvent, None)])
        self.assertEqual(self.service.listSubscriptions(self.cache2),
                         [(IObjectModifiedEvent, None)])

    def test__delitem__(self):
        self.assertEqual(self.service.listSubscriptions(self.cache1),
                         [(IObjectModifiedEvent, None)])
        self.assertEqual(self.service.listSubscriptions(self.cache2),
                         [(IObjectModifiedEvent, None)])
        del self.service['cache1']
        self.assertEqual(self.service.listSubscriptions(self.cache1), [])
        self.assertEqual(self.service.listSubscriptions(self.cache2),
                         [(IObjectModifiedEvent, None)])

        del self.service['cache2']
        self.assertEqual(self.service.listSubscriptions(self.cache2), [])


def test_suite():
    return TestSuite((
        makeSuite(TestCachingService),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
