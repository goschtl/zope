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

$Id: test_cachingservice.py,v 1.12 2003/06/21 21:22:13 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests import setup
from zope.interface.verify import verifyObject
from zope.interface import implements
from zope.app.interfaces.cache.cache import ICache
from zope.app.interfaces.cache.cache import ICachingService
from zope.app.services.cache import CacheRegistration
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.services.tests.eventsetup import EventSetup
from zope.app.traversing import getPath, traverse
from zope.app.interfaces.annotation import IAttributeAnnotatable

def sort(list):
    list.sort()
    return list

class CacheStub:

    implements(ICache, IAttributeAnnotatable)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "CacheStub(%r)" % self.name

    def notify(self, event):
        pass

class CachingServiceSetup(EventSetup):

    def createCachingService(self, path=None):
        from zope.app.services.cache import CachingService

        sm = self.makeSite(path)
        return setup.addService(sm, "Caching", CachingService())

        return service

    def addCache(self, name, cache=None, cname=None, status=ActiveStatus, folder=''):
        if not cache:
            cache = CacheStub("%s/%s" % (folder, name))
        if not cname:
            cname = name
        default = traverse(self.rootFolder, folder +'/++etc++site/default')
        key = default.setObject(cname, cache)
        cache = traverse(default, key)
        configure = default.getRegistrationManager()
        key = configure.setObject('', CacheRegistration(name, getPath(cache)))
        traverse(configure, key).status = status
        return cache


class TestCachingService(CachingServiceSetup, TestCase):

    def setUp(self):
        CachingServiceSetup.setUp(self)
        self.service = self.createCachingService()
        self.cache1 = self.addCache('cache1')
        self.cache2 = self.addCache('cache2')
        self.cache3 = self.addCache('cache3', status=RegisteredStatus)
        self.service_f1 = self.createCachingService('folder1')
        self.cache1_f1 = self.addCache('cache1', folder='folder1')
        self.cache4_f1 = self.addCache('cache4', folder='folder1')

    def test_interface(self):
        from zope.app.services.cache import ILocalCachingService
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
