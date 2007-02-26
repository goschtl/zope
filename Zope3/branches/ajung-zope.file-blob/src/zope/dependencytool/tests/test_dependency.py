##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for zope.dependencytool.dependency.

$Id$
"""
import unittest

from zope.dependencytool.dependency import Dependency


class DependencyTestCase(unittest.TestCase):

    def test_isSubPackageOf(self):
        d1 = Dependency("a.b.c", "filename", 42)
        d2 = Dependency("a.b", "filename", 42)
        d3 = Dependency("a.b.d", "filename", 42)
        d4 = Dependency("a.b.c.d.e", "filename", 42)

        self.assert_(d1.isSubPackageOf(d2))
        self.assert_(d4.isSubPackageOf(d1))
        self.assert_(d4.isSubPackageOf(d2))
        self.assert_(not d1.isSubPackageOf(d1))
        self.assert_(not d2.isSubPackageOf(d1))
        self.assert_(not d1.isSubPackageOf(d3))
        self.assert_(not d3.isSubPackageOf(d1))
        self.assert_(not d1.isSubPackageOf(d4))
        self.assert_(not d2.isSubPackageOf(d4))
        self.assert_(not d3.isSubPackageOf(d4))


def test_suite():
    return unittest.makeSuite(DependencyTestCase)
