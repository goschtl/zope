##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Location support tests

$Id$
"""
import unittest

from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.location.tests import TLocation
from zope.app.fssync import fspickle
from zope.interface import directlyProvides

from zope.testing.doctestunit import DocTestSuite


class PersistentLoaderTestCase(unittest.TestCase):

    def setUp(self):
        root = TLocation()
        directlyProvides(root, IContainmentRoot)
        o1 = TLocation(); o1.__parent__ = root; o1.__name__ = 'o1'
        o2 = TLocation(); o2.__parent__ = root; o2.__name__ = 'o2'
        o3 = TLocation(); o3.__parent__ = o1; o3.__name__ = 'o3'
        root.o1 = o1
        root.o2 = o2
        o1.foo = o2
        o1.o3 = o3
        self.root = root
        self.o1 = o1
        self.o2 = o2

    def testPersistentLoader(self):
        loader = fspickle.PersistentLoader(self.o1)
        self.assert_(loader.load('/') is self.root)
        self.assert_(loader.load('/o2') is self.o2)

    def testParentPersistentLoader(self):
        loader = fspickle.ParentPersistentLoader(self.o1, self.o1)
        self.assert_(loader.load(fspickle.PARENT_MARKER) is self.o1)
        self.assert_(loader.load('/') is self.root)
        self.assert_(loader.load('/o2') is self.o2)


def test_suite():
    suite = unittest.makeSuite(PersistentLoaderTestCase)
    suite.addTest(DocTestSuite('zope.app.fssync.fspickle'))
    return suite

if __name__ == '__main__':
    unittest.main()
