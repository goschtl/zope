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
"""Test the CacheName field

In particular, test the proper getting of cache names in allowed_values.

$Id$
"""
import unittest
from zope.interface import implements

from zope.app.tests import setup
from zope.app.cache.interfaces import CacheName, ICache
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.utility import LocalUtilityService
from zope.thread import thread_globals

class CacheStub(object):
    __name__ = __parent__ = None
    implements(ICache, IAttributeAnnotatable)

    # IAttributeAnnotatable is implemented so that there will be an
    # IDependable adapter available.

class CacheNameTest(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, folders=True)
        sm = self.makeSite()
        thread_globals().site = sm.__parent__
        
        setup.addService(sm, 'Utilities', LocalUtilityService())
        setup.addUtility(sm, 'bar', ICache, CacheStub())
        setup.addUtility(sm, 'baz', ICache, CacheStub())
        setup.addUtility(sm, 'foo', ICache, CacheStub())

    def tearDown(self):
        PlacefulSetup.tearDown(self)
        thread_globals().site = None

    def test(self):
        field = CacheName().bind(self.rootFolder)
        allowed = list(field.allowed_values)
        allowed.sort()
        self.assertEqual(allowed, ['', 'bar', 'baz', 'foo'])


def test_suite():
    return unittest.makeSuite(CacheNameTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
