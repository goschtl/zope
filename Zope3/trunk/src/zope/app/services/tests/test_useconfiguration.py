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
"""
$Id: test_useconfiguration.py,v 1.4 2003/06/12 18:58:50 gvanrossum Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.configuration import UseConfiguration
from zope.app.interfaces.annotation import IAnnotations
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.interface import implements

class C(dict):
    implements(IAnnotations)

class TestUseConfiguration(PlacelessSetup, TestCase):

    def testVerifyInterface(self):
        from zope.interface.verify import verifyObject
        from zope.app.interfaces.services.configuration import \
            IUseConfiguration
        obj = UseConfiguration(C())
        verifyObject(IUseConfiguration, obj)

    def testBasic(self):
        obj = UseConfiguration(C())
        self.failIf(obj.usages())
        obj.addUsage('/a/b')
        obj.addUsage('/c/d')
        obj.addUsage('/c/e')
        obj.addUsage('/c/d')
        locs = list(obj.usages())
        locs.sort()
        self.assertEqual(locs, ['/a/b', '/c/d', '/c/e'])
        obj.removeUsage('/c/d')
        locs = list(obj.usages())
        locs.sort()
        self.assertEqual(locs, ['/a/b', '/c/e'])
        obj.removeUsage('/c/d')
        self.assertEqual(locs, ['/a/b', '/c/e'])

    def testRelativeAbsolute(self):
        obj = UseConfiguration(C())
        # Hack the object to have a parent path
        obj.pp = "/a/"
        obj.pplen = len(obj.pp)
        obj.addUsage("foo")
        self.assertEqual(obj.usages(), ("/a/foo",))
        obj.removeUsage("/a/foo")
        self.assertEqual(obj.usages(), ())
        obj.addUsage("/a/bar")
        self.assertEqual(obj.usages(), ("/a/bar",))
        obj.removeUsage("bar")
        self.assertEqual(obj.usages(), ())

def test_suite():
    return TestSuite((
        makeSuite(TestUseConfiguration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
