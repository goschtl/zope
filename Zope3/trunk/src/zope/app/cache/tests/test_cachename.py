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

$Id: test_cachename.py,v 1.4 2003/06/03 21:42:59 jim Exp $
"""

import unittest

from zope.app.interfaces.cache.cache import CacheName
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.tests import setup
from zope.app.interfaces.services.service import ILocalService

class CachingServiceStub(object):

    __implements__ = ILocalService

    def getAvailableCaches(self):
        return 'foo', 'bar', 'baz'


class CacheNameTest(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, folders=True)
        sm = self.makeSite()
        setup.addService(sm, 'Caching', CachingServiceStub())

    def test(self):
        field = CacheName().bind(self.rootFolder)
        allowed = list(field.allowed_values)
        allowed.sort()
        self.assertEqual(allowed, ['', 'bar', 'baz', 'foo'])


def test_suite():
    return unittest.makeSuite(CacheNameTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
