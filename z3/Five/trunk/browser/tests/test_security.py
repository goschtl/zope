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
"""Test browser security

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, FunctionalTestCase
from Testing.ZopeTestCase import installProduct
installProduct('Five')
installProduct('PythonScripts')  # for RestrictedPythonTestCase

from zope.app import zapi
import Products.Five.browser.tests
from Products.Five import zcml, BrowserView
from Products.Five.traversable import FakeRequest
from Products.Five.testing import RestrictedPythonTestCase
from Products.Five.testing import manage_addFiveTraversableFolder
from Products.Five.tests.test_security import Dummy1
from Products.Five.tests.simplecontent import manage_addSimpleContent

view_names = [
    'eagle.txt',
    'falcon.html',
    'owl.html',
    'flamingo.html',
    'condor.html',
    'protectededitform.html']

public_view_names = [
    'public_attribute_page',
    'public_template_page',
    'public_template_class_page']

ViewManagementScreens = 'View management screens'

class DummyView(BrowserView):
    """A dummy view"""

    def foo(self):
        """A foo"""
        return 'A foo view'

class SecurityTest(RestrictedPythonTestCase):

    def afterSetUp(self):
        zcml.load_config('pages.zcml', package=Products.Five.browser.tests)
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    def test_no_permission(self):
        self.login('viewer')
        for view_name in view_names:
            self.checkUnauthorized(
                'context.restrictedTraverse("testoid/%s")()' % view_name)

    def test_permission(self):
        self.login('manager')
        for view_name in view_names:
            self.check(
                'context.restrictedTraverse("testoid/%s")()' % view_name)

    def test_public_permission(self):
        self.logout()
        for view_name in public_view_names:
            self.check(
                'context.restrictedTraverse("testoid/%s")()' % view_name)

    def test_view_method_permission(self):
        self.login('manager')
        self.check(
            'context.restrictedTraverse("testoid/eagle.method").eagle()')

class PageSecurityTest(ZopeTestCase):

    def test_page_security(self):
        decl = """
        <configure xmlns="http://namespaces.zope.org/zope"
            xmlns:browser="http://namespaces.zope.org/browser">

          <browser:page
             for="Products.Five.tests.test_security.IDummy"
             class="Products.Five.browser.tests.test_security.DummyView"
             attribute="foo"
             name="test_page_security"
             permission="zope2.ViewManagementScreens"
           />

        </configure>
        """
        zcml.load_string(decl)
        request = FakeRequest()
        # Wrap into an acquisition so that imPermissionRole objects
        # can be evaluated.
        view = zapi.getView(Dummy1(), 'test_page_security', request)

        ac = getattr(view, '__ac_permissions__')
        # It's protecting the object with the permission, and not the
        # attribute, so we get ('',) instead of ('foo',).
        ex_ac = (('View management screens', ('',)),)
        self.assertEquals(ac, ex_ac)

        # Wrap into an acquisition so that imPermissionRole objects
        # can be evaluated. __roles__ is a imPermissionRole object.
        view = view.__of__(self.folder)
        view_roles = getattr(view, '__roles__', None)
        self.failIf(view_roles is None)
        self.failIf(view_roles == ())
        self.assertEquals(view_roles, ('Manager',))

class PublishSecurityTest(FunctionalTestCase):
    """A functional test for security actually involving the publisher.
    """
    def afterSetUp(self):
        zcml.load_config('pages.zcml', package=Products.Five.browser.tests)
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    def test_no_permission(self):
        for view_name in view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name,
                                    basic='viewer:secret')
            # we expect that we get a 401 Unauthorized
            status = response.getStatus()
            self.failUnless(status == 401, (status, 401, view_name))

    def test_all_permissions(self):
        permissions = self.folder.possible_permissions()
        self.folder._addRole('Viewer')
        self.folder.manage_role('Viewer', permissions)
        self.folder.manage_addLocalRoles('viewer', ['Viewer'])

        for view_name in view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name,
                                    basic='viewer:secret')
            status = response.getStatus()
            self.failUnless(status == 200, (status, 200, view_name))

    def test_almost_all_permissions(self):
        permissions = self.folder.possible_permissions()
        permissions.remove(ViewManagementScreens)
        self.folder._addRole('Viewer')
        self.folder.manage_role('Viewer', permissions)
        self.folder.manage_addLocalRoles('viewer', ['Viewer'])

        for view_name in view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name,
                                    basic='viewer:secret')
            # we expect that we get a 401 Unauthorized
            status = response.getStatus()
            self.failUnless(status == 401, (status, 401, view_name))

    def test_manager_permission(self):
        for view_name in view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name,
                                    basic='manager:r00t')
            # we expect that we get a 200 Ok
            self.assertEqual(response.getStatus(), 200)

    def test_public_permission(self):
        for view_name in public_view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name)
            status = response.getStatus()
            self.failUnless(status == 200, (status, 200, view_name))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityTest))
    suite.addTest(unittest.makeSuite(PageSecurityTest))
    suite.addTest(unittest.makeSuite(PublishSecurityTest))
    return suite

if __name__ == '__main__':
    framework()
