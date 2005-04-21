##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test edit forms

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import FunctionalTestCase, installProduct
installProduct('Five')

from AccessControl import Unauthorized
from zope.app.form.browser.submit import Update

import Products.Five.form.tests
from Products.Five import zcml
from Products.Five.tests.helpers import manage_addFiveTraversableFolder
from Products.Five.form.tests.schemacontent import manage_addFieldContent
from Products.Five.form.tests.schemacontent import manage_addComplexSchemaContent

class EditFormTest(FunctionalTestCase):

    def afterSetUp(self):
        manage_addFieldContent(self.folder, 'edittest', 'Test')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        zcml.load_config('configure.zcml', package=Products.Five.form.tests)

    def test_editform(self):
        response = self.publish('/test_folder_1_/edittest/edit.html',
                                basic='manager:r00t')
        # we're using a GET request to post variables, but seems to be
        # the easiest..
        response = self.publish(
            '/test_folder_1_/edittest/edit.html?%s=1&field.title=FooTitle&field.description=FooDescription' % Update,
            basic='manager:r00t')
        self.assertEquals('FooTitle', self.folder.edittest.title)
        self.assertEquals('FooDescription', self.folder.edittest.description)

    def test_editform_invalid(self):
        # missing title, which is required
        self.folder.edittest.description = ''

        response = self.publish(
            '/test_folder_1_/edittest/edit.html?%s=1&field.title=&field.description=BarDescription' % Update,
            basic='manager:r00t')
        # we expect that we get a 200 Ok
        self.assertEqual(200, response.getStatus())
        self.assertEquals('Test', self.folder.edittest.title)
        self.assertEquals('', self.folder.edittest.description)

    def test_addform(self):
        manage_addFiveTraversableFolder(self.folder, 'ftf')
        self.folder = self.folder.ftf
        response = self.publish('/test_folder_1_/ftf/+/addsimplecontent.html',
                                basic='manager:r00t')
        self.assertEquals(200, response.getStatus())
        # we're using a GET request to post variables, but seems to be
        # the easiest..
        response = self.publish(
            '/test_folder_1_/ftf/+/addsimplecontent.html?%s=1&add_input_name=alpha&field.title=FooTitle&field.description=FooDescription' % Update,
            basic='manager:r00t')
        # we expect to get a 302 (redirect)
        self.assertEquals(302, response.getStatus())
        # we expect the object to be there with the right id
        self.assertEquals('alpha', self.folder.alpha.id)
        self.assertEquals('FooTitle', self.folder.alpha.title)
        self.assertEquals('FooDescription', self.folder.alpha.description)

    def test_objectWidget(self):
        manage_addComplexSchemaContent(self.folder, 'ftf')
        response = self.publish('/test_folder_1_/ftf/edit.html',
                                basic='manager:r00t')
        self.assertEquals(200, response.getStatus())

    def test_addpages(self):
        manage_addFiveTraversableFolder(self.folder, 'ftf')

        # Unprotected as anonymous
        response = self.publish('/test_folder_1_/ftf/+/addsimplecontent.html')
        self.assertEqual(response.getStatus(), 200)
        
        # Protected as manager
        response = self.publish('/test_folder_1_/ftf/+/protectedaddform.html',
                                basic='manager:r00t')
        self.assertEqual(response.getStatus(), 200)

        # Protected as user
        response = self.publish('/test_folder_1_/ftf/+/protectedaddform.html',
                                basic='viewer:secret')
        self.assertEqual(response.getStatus(), 401)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EditFormTest))
    return suite

if __name__ == '__main__':
    framework()
