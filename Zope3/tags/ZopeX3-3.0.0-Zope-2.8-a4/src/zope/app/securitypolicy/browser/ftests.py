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

$Id: ftests.py 25177 2004-06-02 13:17:31Z jim $
"""
import unittest
from zope.app.tests.functional import BrowserTestCase

class GrantTest(BrowserTestCase):

    def testGrant(self):
        response = self.publish(
            '/@@grant.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Grant permissions to roles' in body)
        self.assert_('Grant roles to principals' in body)
        self.checkForBrokenLinks(body, '/@@grant.html', 'mgr:mgrpw')


class RolePermissionsTest(BrowserTestCase):

    def testAllRolePermissionsForm(self):
        response = self.publish(
            '/@@AllRolePermissions.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Permissions' in body)
        self.assert_('Manage Content' in body)
        self.assert_('Manage Services' in body)
        self.assert_('Roles' in body)
        self.assert_('Site Manager' in body)
        self.assert_('Site Member' in body)
        self.failIf(_result in body)
        self.checkForBrokenLinks(body, '/@@AllRolePermissions.html',
                                 'mgr:mgrpw')

    def testAllRolePermissions(self):
        response = self.publish(
            '/@@AllRolePermissions.html',
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
            '/@@RolesWithPermissions.html?permission_to_manage=zope.View',
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
            '/@@RolePermissions.html?role_to_manage=zope.Manager',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_(
            'This page shows the permissions allowed and denied the role'
            in body)
        self.assert_('Allow' in body)
        self.assert_('Deny' in body)
        self.checkForBrokenLinks(body, '/@@RolesPermissions.html',
                                 'mgr:mgrpw')

_result = '''\
            <option value="Unset"> </option>
            <option value="Allow" selected="selected">+</option>
            <option value="Deny">-</option>
'''

class PrincipalRolesTest(BrowserTestCase):

    def testPrincipalRolesForm(self):
        response = self.publish(
            '/@@PrincipalRoles.html',
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Apply filter' in body)
        self.assert_('Principal(s)' in body)
        self.assert_('Role(s)' in body)
        self.assert_('"Filter"' in body)
        self.checkForBrokenLinks(body, '/@@PrincipalRoles.html',
                                 'mgr:mgrpw')

    def testPrincipalRoles(self):
        response = self.publish(
            '/@@PrincipalRoles.html',
            form={'principals': ['zope.mgr'],
                  'roles': ['zope.Member', 'zope.Manager'],
                  'Filter': 'Filter'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('zope.mgr' in body)
        self.assert_('zope.Member' in body)
        self.assert_('"APPLY"' in body)
        self.failIf(_result in body)
        self.checkForBrokenLinks(body, '/@@PrincipalRoles.html',
                                 'mgr:mgrpw')

    def testPrincipalRolesApply(self):
        response = self.publish(
            '/@@PrincipalRoles.html',
            form={'principals': ['zope.mgr'],
                  'roles': ['zope.Member', 'zope.Manager'],
                  'grid.zope.Member.zope.mgr': 'Allow', 
                  'APPLY': 'Apply'},
            basic='mgr:mgrpw')
        self.assertEqual(response.getStatus(), 200)
        body = response.getBody()
        self.assert_('Apply filter' in body)
        self.assert_('Principal(s)' in body)
        self.assert_('Role(s)' in body)
        self.assert_('"Filter"' in body)
        self.checkForBrokenLinks(body, '/@@PrincipalRoles.html',
                                 'mgr:mgrpw')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(GrantTest),
        unittest.makeSuite(RolePermissionsTest),
        unittest.makeSuite(PrincipalRolesTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
