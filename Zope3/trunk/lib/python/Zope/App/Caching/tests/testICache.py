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

$Id: testICache.py,v 1.2 2002/10/31 16:01:40 alga Exp $
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
        self.failIf(cache.query(ob, default=marker) is not marker,
                    "empty cache should not contain anything")

        cache.set(data, ob, view_name="view1")
        self.assertEquals(cache.query(ob, "view1"), data,
                    "should return cached result")
        self.failIf(cache.query(ob, "view2", default=marker) is not marker,
                    "should not return cached result for a different view")

        cache.invalidate(ob, "view2")
        self.assertEquals(cache.query(ob, "view1"), data,
                    "should return cached result")
        self.failIf(cache.query(ob, "view2", default=marker) is not marker,
                    "should not return cached result for a different view")

        cache.invalidate(ob, "view1")
        self.failIf(cache.query(ob, "view1", default=marker) is not marker,
                    "should not return cached result after invalidate")

# TODO: test all cases of invalidate (all, only view, view and keywords)
#       test set/query with keywords
#       test uses of mtime_func

# So far there are no classes implementing ICache, so running the tests will
# have to be deferred

def test_suite():
    return TestSuite((
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')




