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
from Zope.App.Security.RolePermissionView import RolePermissionView
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

    def testGrant(self):
        roles = self.view.roles()
        permissions = self.view.permissions()

        self.view.action({
            'p0': 'read', 'p1': 'write',
            'r0': 'manager', 'r1': 'member',
            'p0r0': '1', 'p0r1': '1', 'p1r0': '1',
            },
                         testing=1)
        permissionRoles = self.view.permissionRoles()
        for ip in range(len(permissionRoles)):
            permissionRole = permissionRoles[ip]
            rset = permissionRole.roles()
            for ir in range(len(rset)):
                setting = rset[ir]
                if setting is None:
                    self.failIf(
                        roles[ir].getId()  == 'manager'
                        or
                        permissions[ip].getId() == 'read'
                        )
                else:
                    self.failUnless(
                        roles[ir].getId()  == 'manager'
                        or
                        permissions[ip].getId() == 'read'
                        )

        self.view.action({
            'p0': 'read', 'p1': 'write',
            'r0': 'manager', 'r1': 'member',
            'p0r0': '1',
            },
                         testing=1)
        permissionRoles = self.view.permissionRoles()
        for ip in range(len(permissionRoles)):
            permissionRole = permissionRoles[ip]
            rset = permissionRole.roles()
            for ir in range(len(rset)):
                setting = rset[ir]
                if setting is None:
                    self.failIf(
                        roles[ir].getId()  == 'manager'
                        and
                        permissions[ip].getId() == 'read'
                        )
                else:
                    self.failUnless(
                        roles[ir].getId()  == 'manager'
                        and
                        permissions[ip].getId() == 'read'
                        )
        

        self.view.update_permission(REQUEST=None,
                                    permission_id='write',
                                    roles=['member'],
                                    testing=1)

        permission = self.view.permissionForID('write')
        self.assertEquals(
            [r['id']
             for r in permission.rolesInfo()
             if r['checked']],
            ['member'])
        
        self.view.update_permission(REQUEST=None,
                                    permission_id='write',
                                    # roles=[],  roles attr omitted
                                    testing=1)

        permission = self.view.permissionForID('write')
        self.assertEquals(
            [r['id']
             for r in permission.rolesInfo()
             if r['checked']],
            [])

            
        self.view.update_permission(REQUEST=None,
                                    permission_id='write',
                                    roles=['manager','member'],
                                    testing=1)

        permission = self.view.permissionForID('write')
        result = [r['id']
                  for r in permission.rolesInfo()
                  if r['checked']]
        what_result_should_be = ['manager','member']
        result.sort()
        what_result_should_be.sort()
        self.assertEquals(
            result,
            what_result_should_be
            )

        self.view.update_role(REQUEST=None,
                              role_id='member',
                              permissions=['write','read'],
                              testing=1)

        role = self.view.roleForID('member')
        result = [r['id']
                  for r in role.permissionsInfo()
                  if r['checked']]
        what_result_should_be = ['write','read']
        result.sort()
        what_result_should_be.sort()
        self.assertEquals(
            result,
            what_result_should_be
            )

        self.view.update_role(REQUEST=None,
                              role_id='member',
                              # omitted attribute permissions,
                              testing=1)

        role = self.view.roleForID('member')
        result = [r['id']
                  for r in role.permissionsInfo()
                  if r['checked']]
        what_result_should_be = []
        result.sort()
        what_result_should_be.sort()
        self.assertEquals(
            result,
            what_result_should_be
            )



def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
