##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
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
