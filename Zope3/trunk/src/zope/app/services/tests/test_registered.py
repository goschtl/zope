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
$Id: test_registered.py,v 1.2 2003/09/21 17:31:13 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.registration import Registered
from zope.app.interfaces.annotation import IAnnotations
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.interface import implements
from zope.app.container.contained import Contained

class C(dict, Contained):
    implements(IAnnotations)

class TestRegistered(PlacelessSetup, TestCase):

    def testVerifyInterface(self):
        from zope.interface.verify import verifyObject
        from zope.app.interfaces.services.registration import IRegistered
        obj = Registered(C())
        verifyObject(IRegistered, obj)

    def testBasic(self):
        obj = Registered(C())
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
        locs = list(obj.usages())
        locs.sort()
        self.assertEqual(locs, ['/a/b', '/c/e'])

    def testRelativeAbsolute(self):
        obj = Registered(C())
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
    return makeSuite(TestRegistered)

if __name__=='__main__':
    main(defaultTest='test_suite')
