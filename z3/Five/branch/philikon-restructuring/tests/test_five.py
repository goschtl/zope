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
from Testing.ZopeTestCase import ZopeTestCase, FunctionalTestCase
from Testing.ZopeTestCase import installProduct
installProduct('Five')

import Products.Five.tests
from Products.Five import zcml

from Products.Five.tests.adapters import IAdapted, IDestination
from Products.Five.tests.adapters import Adaptable, Origin
from Products.Five.tests.simplecontent import manage_addSimpleContent
from Products.Five.tests.fancycontent import manage_addFancyContent

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

class PublishDirectivesTest(FunctionalTestCase):
    """Test a few publishing features"""

    def afterSetUp(self):
        zcml.load_config('directives.zcml', package=Products.Five.tests)
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    def test_no_doc_string(self):
        for view_name in ['nodoc-function', 'nodoc-method', 'nodoc-object']:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name)
            self.assertEquals("No docstring", response.getBody())

    def test_fallback_raises_notfound(self):
        # If we return None in __fallback_traverse__, this test passes
        # but for the wrong reason: None doesn't have a docstring so
        # BaseRequest raises NotFoundError. A functional test would be
        # perfect here.
        response = self.publish('/test_folder_1_/testoid/doesntexist')
        self.assertEquals(404, response.getStatus())

    def test_existing_bobo_traverse(self):
        manage_addFancyContent(self.folder, 'fancy', '')

        # check if the old bobo_traverse method can still kick in
        response = self.publish('/test_folder_1_/fancy/something-else')
        self.assertEquals('something-else', response.getBody())

        # check if z3-based view lookup works
        response = self.publish('/test_folder_1_/fancy/fancy')
        self.assertEquals("Fancy, fancy", response.getBody())

    def test_pages_from_directory(self):
        response = self.publish('/test_folder_1_/testoid/dirpage1')
        self.assert_('page 1' in response.getBody())
        response = self.publish('/test_folder_1_/testoid/dirpage2')
        self.assert_('page 2' in response.getBody())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DirectivesTest))
    suite.addTest(unittest.makeSuite(PublishDirectivesTest))
    return suite

if __name__ == '__main__':
    framework()
