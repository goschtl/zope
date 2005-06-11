##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Test the basic ZCML directives

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

import Products.Five.tests
from Products.Five import zcml

from Products.Five.tests.adapters import IAdapted, IDestination
from Products.Five.tests.adapters import Adaptable, Origin
from Products.Five.tests.simplecontent import manage_addSimpleContent

class DirectivesTest(ZopeTestCase):
    """Test very basic Five functionality (adapters, ZCML, etc.)"""

    def afterSetUp(self):
        zcml.load_config('directives.zcml', package=Products.Five.tests)

    def test_adapters(self):
        obj = Adaptable()
        adapted = IAdapted(obj)
        self.assertEquals(
            "Adapted: The method",
            adapted.adaptedMethod())

    def test_overrides(self):
        zcml.load_string(
            """<includeOverrides
                   package="Products.Five.tests"
                   file="overrides.zcml" />""")
        origin = Origin()
        dest = IDestination(origin)
        self.assertEquals(dest.method(), "Overridden")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DirectivesTest))
    return suite

if __name__ == '__main__':
    framework()
