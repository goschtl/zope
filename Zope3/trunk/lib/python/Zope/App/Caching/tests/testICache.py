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
"""Unit tests for ICache interface

$Id: testICache.py,v 1.3 2002/11/25 13:48:06 alga Exp $
"""

from unittest import TestSuite, main
from Interface.Verify import verifyObject
from Zope.App.Caching.ICache import ICache


class BaseICacheTest:
    """Base class for ICache unit tests.  Subclasses should provide a
    _Test__new() method that returns a new empty cache object.
    """

    def testVerifyICache(self):
        """Verify that the object implements ICache"""
        verifyObject(ICache, self._Test__new())

    def testCaching(self):
        """Verify basic caching"""
        cache = self._Test__new()
        ob = "obj"
        data = "data"
        marker = []
        self.failIf(cache.query(ob, None, default=marker) is not marker,
                    "empty cache should not contain anything")

        cache.set(data, ob, key={'id': 35})
        self.assertEquals(cache.query(ob, {'id': 35}), data,
                    "should return cached result")
        self.failIf(cache.query(ob, {'id': 33}, default=marker) is not marker,
                    "should not return cached result for a different key")

        cache.invalidate(ob, {"id": 33})
        self.assertEquals(cache.query(ob, {'id': 35}), data,
                          "should return cached result")
        self.failIf(cache.query(ob, {'id': 33}, default=marker) is not marker,
                    "should not return cached result after invalidate")

def test_suite():
    return TestSuite((
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')




