##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import unittest, sys
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup\
           import PlacefulSetup
from Zope.ComponentArchitecture import getServiceManager
from Zope.App.Security.IRoleService import IRoleService
from RoleService import RoleService
from PermissionService import PermissionService
from RolePermissionManager import RolePermissionManager
from Zope.App.Security.Grants.Views.Browser.RolePermissionView \
     import RolePermissionView
from Zope.App.Security.IPermissionService import IPermissionService

class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        defineService=getServiceManager(None).defineService
        provideService=getServiceManager(None).provideService
        defineService('RoleService', IRoleService)
        provideService('RoleService', RoleService(
            manager='Manager', member='Member'))
        defineService('PermissionService', IPermissionService)
        provideService('PermissionService', PermissionService(
            read='Read', write='Write'))
        self.view = RolePermissionView(RolePermissionManager(), None)

    def testRoles(self):
        roles = list(self.view.roles())
        ids = ['manager', 'member']
        titles = ['Manager', 'Member']
        for role in roles:
            i=ids.index(role.getId())
            self.failIf(i < 0)
            self.assertEqual(role.getTitle(), titles[i])
            del ids[i]
            del titles[i]

    def testPermisssions(self):
        permissions = list(self.view.permissions())
        ids = ['read', 'write']
        titles = ['Read', 'Write']
        for permission in permissions:
            i=ids.index(permission.getId())
            self.failIf(i < 0)
            self.assertEqual(permission.getTitle(), titles[i])
            del ids[i]
            del titles[i]

    def testMatrix(self):
        roles = self.view.roles()
        permissions = self.view.permissions()

        #         manager  member
        # read       +
        # write      .       -
        REQ = {
            'p0': 'read', 'p1': 'write',
            'r0': 'manager', 'r1': 'member',
            'p0r0': 'Allow',
            'p1r0': 'Unset', 'p1r1': 'Deny',
            }
        self.view.request = REQ # XXX yuck
        self.view.action(testing=1)
        permissionRoles = self.view.permissionRoles()
        for ip in range(len(permissionRoles)):
            permissionRole = permissionRoles[ip]
            rset = permissionRole.roleSettings()
            for ir in range(len(rset)):
                setting = rset[ir]
                r = roles[ir].getId()
                p = permissions[ip].getId()
                if setting == 'Allow':
                    self.failUnless(r == 'manager' and p == 'read')
                elif setting == 'Deny':
                    self.failUnless(r == 'member' and p == 'write')
                else:
                    self.failUnless(setting == 'Unset')

        #         manager  member
        # read       -
        # write      +
        REQ = {
            'p0': 'read', 'p1': 'write',
            'r0': 'manager', 'r1': 'member',
            'p0r0': 'Deny',
            'p1r0': 'Allow', 'p1r1': 'Unset'
            }
        self.view.request = REQ # XXX yuck
        self.view.action(testing=1)
        permissionRoles = self.view.permissionRoles()
        for ip in range(len(permissionRoles)):
            permissionRole = permissionRoles[ip]
            rset = permissionRole.roleSettings()
            for ir in range(len(rset)):
                setting = rset[ir]
                r = roles[ir].getId()
                p = permissions[ip].getId()
                if setting == 'Allow':
                    self.failUnless(r == 'manager' and p == 'write')
                elif setting == 'Deny':
                    self.failUnless(r == 'manager' and p == 'read')
                else:
                    self.failUnless(setting == 'Unset')

    def testPermissionRoles(self):
        self.view.update_permission(permission_id='write',
                                    settings=['Allow', 'Unset'],
                                    testing=1)
        permission = self.view.permissionForID('write')
        settings = permission.roleSettings()
        self.assertEquals(settings, ['Allow', 'Unset'])


        self.view.update_permission(permission_id='write',
                                    settings=['Unset', 'Deny'],
                                    testing=1)
        permission = self.view.permissionForID('write')
        settings = permission.roleSettings()
        self.assertEquals(settings, ['Unset', 'Deny'])

        self.assertRaises(ValueError,
                          self.view.update_permission,
                          permission_id='write',
                          settings=['Unset', 'foo'],
                          testing=1)

    def testRolePermissions(self):
        REQ={'Allow': ['read'],
             'Deny': ['write']}
        self.view.request = REQ # XXX yuck
        self.view.update_role(role_id='member',
                              testing=1)
        role = self.view.roleForID('member')
        pinfos = role.permissionsInfo()
        for pinfo in pinfos:
            pid = pinfo['id']
            if pid == 'read':
                self.assertEquals(pinfo['setting'], 'Allow')
            if pid == 'write':
                self.assertEquals(pinfo['setting'], 'Deny')

        REQ={'Allow': [],
             'Deny': ['read']}
        self.view.request = REQ # XXX yuck
        self.view.update_role(role_id='member',
                              testing=1)
        role = self.view.roleForID('member')
        pinfos = role.permissionsInfo()
        for pinfo in pinfos:
            pid = pinfo['id']
            if pid == 'read':
                self.assertEquals(pinfo['setting'], 'Deny')
            if pid == 'write':
                self.assertEquals(pinfo['setting'], 'Unset')


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
