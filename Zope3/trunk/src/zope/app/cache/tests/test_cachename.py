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

$Id: test_cachename.py,v 1.2 2002/12/25 14:12:45 jim Exp $
"""

import unittest

from zope.proxy.context import ContextWrapper

from zope.app.interfaces.cache.cache import CacheName
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.tests.servicemanager import TestingServiceManager

class CachingServiceStub(object):

    def getAvailableCaches(self):
        return 'foo', 'bar', 'baz'


class CacheNameTest(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        sm = TestingServiceManager()
        self.rootFolder.setServiceManager(sm)
        sm.Caching = CachingServiceStub()

    def test(self):
        field = CacheName().bind(self.rootFolder)
        allowed = list(field.allowed_values)
        allowed.sort()
        self.assertEqual(allowed, ['', 'bar', 'baz', 'foo'])


def test_suite():
    return unittest.makeSuite(CacheNameTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
