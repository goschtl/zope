##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test Default View functionality

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import FunctionalTestCase, installProduct
installProduct('Five')

import Products.Five.browser.tests
from Products.Five import zcml
from Products.Five.tests.simplecontent import manage_addSimpleContent
from Products.Five.tests.simplecontent import manage_addCallableSimpleContent
from Products.Five.tests.simplecontent import manage_addIndexSimpleContent

class DefaultViewTest(FunctionalTestCase):

    def afterSetUp(self):
        zcml.load_config('defaultview.zcml', package=Products.Five.browser.tests)
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        manage_addCallableSimpleContent(self.folder, 'testcall', 'TestCall')
        manage_addIndexSimpleContent(self.folder, 'testindex', 'TestIndex')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    # Disabled __call__ overriding for now. Causes more trouble
    # than it fixes.

    # def test_existing_call(self):
    #     response = self.publish('/test_folder_1_/testcall')
    #     self.assertEquals("Default __call__ called", response.getBody())

    def test_existing_index(self):
        response = self.publish('/test_folder_1_/testindex')
        self.assertEquals("Default index_html called", response.getBody())

    def test_default_view(self):
        response = self.publish('/test_folder_1_/testoid', basic='manager:r00t')
        self.assertEquals("The eagle has landed", response.getBody())

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DefaultViewTest))
    return suite

if __name__ == '__main__':
    framework()
