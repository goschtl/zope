##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Unit tests for BundleView class.

XXX Incomplete.

$Id: tests.py,v 1.2 2004/03/13 21:03:06 srichter Exp $
"""
import unittest

from zope.interface import implements
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.bundle.browser import BundleView


class SampleClass(object):

    implements(IPhysicallyLocatable)

    def __init__(self, path="/foo"):
        self.path = path

    def getPath(self):
        return self.path

    def items(self):
        return []


class TestBundleView(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(TestBundleView, self).setUp()

    def test_parseVersion(self):
        bv = BundleView(SampleClass(), None)
        pv = bv.parseVersion
        self.assertEquals(pv("/foo/bar-666"), ["f000000666", "f"])
        self.assertEquals(pv("/foo/bar-1.0"),
                          ["f000000001", "f000000000", "f"])
        self.assertEquals(pv("foo-bar-2.3.4"),
                          ["f000000002", "f000000003", "f000000004", "f"])
        self.assertEquals(pv("bar-5.6.a7"), ["f000000005", "f000000006", "a7"])
        self.assertEquals(pv("foo"), None)
        self.assertEquals(pv("foo-bar"), None)
        self.assertEquals(pv("foo.1.0"), None)
        self.assertEquals(pv("foo-1.a1.0"), None)

    def test_inOlderVersion(self):
        bv = BundleView(SampleClass("/++etc++site/foo-bar-1.0.0"), None)
        iov = bv.inOlderVersion
        self.failUnless(iov(SampleClass("/++etc++site/foo-bar-0.9/RM/1")))
        self.failIf(iov(SampleClass("/++etc++site/bar-foo-0.9/RM/2")))
        self.failIf(iov(SampleClass("/++etc++site/foo-bar-1.1/RM/3")))

    def test_listServices(self):
        bv = BundleView(SampleClass("/++etc++site/foo-bar-1.0.0"), None)
        infos = bv.listServices()
        self.assertEquals(infos, [])

    def test_listRegistrations(self):
        bv = BundleView(SampleClass("/++etc++site/foo-bar-1.0.0"), None)
        infos = bv.listRegistrations()
        self.assertEquals(infos, [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestBundleView))
    return suite

if __name__ == '__main__':
    unittest.main()
