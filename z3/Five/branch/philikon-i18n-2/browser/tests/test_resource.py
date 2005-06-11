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
"""Test browser resources

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, FunctionalTestCase
from Testing.ZopeTestCase import installProduct
installProduct('Five')
installProduct("PythonScripts")  # for SecurityResourceTests

import glob
import Products.Five.browser.tests
from Products.Five import zcml
from Products.Five.browser.resource import Resource, PageTemplateResource
from Products.Five.testing import manage_addFiveTraversableFolder
from Products.Five.testing import RestrictedPythonTestCase

_prefix = os.path.dirname(Products.Five.browser.tests.__file__)
dir_resource_names = [os.path.basename(r)
                      for r in (glob.glob('%s/*.png' % _prefix) +
                                glob.glob('%s/*.pt' % _prefix) +
                                glob.glob('%s/[a-z]*.py' % _prefix) +
                                glob.glob('%s/*.css' % _prefix))]

class ResourceTests(ZopeTestCase):

    def afterSetUp(self):
        zcml.load_config('resource.zcml', package=Products.Five.browser.tests)
        manage_addFiveTraversableFolder(self.folder, 'testoid', 'Testoid')

    def test_template_resource(self):
        resource = self.folder.unrestrictedTraverse('testoid/++resource++cockatiel.html')
        self.assert_(isinstance(resource, Resource))
        expected = 'http://nohost/test_folder_1_/testoid/++resource++cockatiel.html'
        self.assertEquals(expected, resource())

    def test_file_resource(self):
        resource = self.folder.unrestrictedTraverse('testoid/++resource++style.css')
        self.assert_(isinstance(resource, Resource))
        expected = 'http://nohost/test_folder_1_/testoid/++resource++style.css'
        self.assertEquals(expected, resource())

    def test_image_resource(self):
        resource = self.folder.unrestrictedTraverse('testoid/++resource++pattern.png')
        expected = 'http://nohost/test_folder_1_/testoid/++resource++pattern.png'
        self.assert_(isinstance(resource, Resource))
        self.assertEquals(expected, resource())

    def test_resource_directory(self):
        base = 'testoid/++resource++fivetest_resources/%s'
        base_url = 'http://nohost/test_folder_1_/' + base

        abs_url = self.folder.unrestrictedTraverse(base % '')()
        self.assertEquals(abs_url + '/', base_url % '')

        for r in dir_resource_names:
            resource = self.folder.unrestrictedTraverse(base % r)
            self.assert_(isinstance(resource, Resource))
            # PageTemplateResource's __call__ renders the template
            if not isinstance(resource, PageTemplateResource):
                self.assertEquals(resource(), base_url % r)

class PublishResourceTests(FunctionalTestCase):

    def afterSetUp(self):
        zcml.load_config('resource.zcml', package=Products.Five.browser.tests)
        manage_addFiveTraversableFolder(self.folder, 'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    def test_publish_image_resource(self):
        url = '/test_folder_1_/testoid/++resource++pattern.png'
        response = self.publish(url, basic='manager:r00t')
        self.assertEquals(200, response.getStatus())

    def test_publish_file_resource(self):
        url = '/test_folder_1_/testoid/++resource++style.css'
        response = self.publish(url, basic='manager:r00t')
        self.assertEquals(200, response.getStatus())

    def test_publish_template_resource(self):
        url = '/test_folder_1_/testoid/++resource++cockatiel.html'
        response = self.publish(url, basic='manager:r00t')
        self.assertEquals(200, response.getStatus())

    def test_publish_resource_directory(self):
        base_url = '/test_folder_1_/testoid/++resource++fivetest_resources/%s'
        for r in dir_resource_names:
            if r.endswith('.pt'):
                # page templates aren't guaranteed to render
                continue
            response = self.publish(base_url % r, basic='manager:r00t')
            self.assertEquals(200, response.getStatus())

resource_names = [
    'cockatiel.html',
    'style.css',
    'pattern.png'
    ]

class SecurityResourceTests(RestrictedPythonTestCase):

    def afterSetUp(self):
        zcml.load_config('resource.zcml', package=Products.Five.browser.tests)
        manage_addFiveTraversableFolder(self.folder, 'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    def test_resource_no_permission(self):
        self.login('viewer')
        for resource in resource_names:
            self.checkUnauthorized(
                'context.restrictedTraverse("testoid/++resource++%s")()' %
                resource)

    def test_directory_resource_no_permission(self):
        self.login('viewer')
        base = 'testoid/++resource++fivetest_resources/%s'
        for resource in dir_resource_names:
            path = base % resource
            self.checkUnauthorized('context.restrictedTraverse("%s")' % path)

    def test_resource_permission(self):
        self.login('manager')
        for resource in resource_names:
            self.check(
                'context.restrictedTraverse("testoid/++resource++%s")()' %
                resource)

    def test_directory_resource_permission(self):
        self.login('manager')
        base = 'testoid/++resource++fivetest_resources/%s'
        for resource in dir_resource_names:
            path = base % resource
            self.check('context.restrictedTraverse("%s")' % path)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResourceTests))
    suite.addTest(unittest.makeSuite(PublishResourceTests))
    suite.addTest(unittest.makeSuite(SecurityResourceTests))
    return suite

if __name__ == '__main__':
    framework()
