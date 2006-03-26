##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""Functional tests for Security Policy's Grant screens.

$Id$
"""
import unittest

from zope.app.testing import functional
from zope.app.security.interfaces import IPermission
from zope.app.security.permission import Permission
from zope.app.securitypolicy.role import Role
from zope.app.securitypolicy.interfaces import IRole
from zope.app.tests import ztapi


class RolePermissionsTest(functional.BrowserTestCase):

    def testAllRolePermissionsForm(self):
        response = self.publish(
            '/++etc++site/@@AllRolePermissions.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Permissions' in body)
        self.assert_('Manage Content' in body)
        self.assert_('Manage Site' in body)
        self.assert_('Roles' in body)
        self.assert_('Site Manager' in body)
        self.assert_('Site Member' in body)
        self.failIf(_result in body)
        self.checkForBrokenLinks(body,
                                 '/++etc++site/@@AllRolePermissions.html',
                                 'mgr:mgrpw')

    def testAllRolePermissions(self):
        response = self.publish(
            '/++etc++site/@@AllRolePermissions.html',
            form={'p0r0': 'Allow',
                  'p0': 'zope.ManageContent',
                  'r0': 'zope.Manager',
                  'SUBMIT': 'Save Changes'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('<p>Settings changed' in body)
        self.assert_(_result in body)

    def testRolesWithPermissionsForm(self):
        response = self.publish(
            '/++etc++site/@@RolesWithPermissions.html'
            '?permission_to_manage=zope.View',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Roles assigned to the permission' in body)
        self.assert_('Role' in body)
        self.assert_('Setting' in body)
        self.assert_('"Save Changes"' in body)
        self.checkForBrokenLinks(body, '/@@RolesWithPermissions.html',
                                 'mgr:mgrpw')

    def testRolesWithPermissionsForm(self):
        response = self.publish(
            '/++etc++site/@@RolePermissions.html?role_to_manage=zope.Manager',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(
            'This page shows the permissions allowed and denied the role'
            in body)
        self.assert_('Allow' in body)
        self.assert_('Deny' in body)
        self.checkForBrokenLinks(body, '/++etc++site/@@RolesPermissions.html',
                                 'mgr:mgrpw')

    def testAllRolePermissionsFormForLocalRoles(self):
        role = Role(u"id", u"Local Role")
        ztapi.provideUtility(IRole, role)
        self.testAllRolePermissions()

        response = self.publish(
            '/++etc++site/@@AllRolePermissions.html',
            basic='mgr:mgrpw')
        body = response.getBody()
        self.assert_('Local Role' in body)

    def testAllRolePermissionsFormForLocalPermissions(self):
        permission = Permission(u"id", u"Local Permission")
        ztapi.provideUtility(IPermission, permission)
        self.testAllRolePermissions()

        response = self.publish(
            '/++etc++site/@@AllRolePermissions.html',
            basic='mgr:mgrpw')
        body = response.getBody()
        self.assert_('Local Permission' in body)

    def testRolesWithPermissionsFormForLocalPermission(self):
        permission = Permission(u"id", u"Local Permission")
        ztapi.provideUtility(IPermission, permission)

        response = self.publish(
            '/++etc++site/@@AllRolePermissions.html',
            form={'role_id': 'zope.Manager',
                  'Allow': ['id'],
                  'Deny': ['id'],
                  'SUBMIT_ROLE': 'Save Changes'},
            basic='mgr:mgrpw',
            handle_errors=True)
        body = response.getBody()
        self.assert_('You choose both allow and deny for permission'
            ' "Local Permission". This is not allowed.' in body)

_result = '''\
            <option value="Unset"> </option>
            <option value="Allow" selected="selected">+</option>
            <option value="Deny">-</option>
'''

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(RolePermissionsTest),
        functional.FunctionalDocFileSuite('granting_ftest.txt'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
