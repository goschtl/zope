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
"""Test handler for RolePermissionManager module."""

import sys
import unittest

from zope.component.service import serviceManager as services
from zope.app.services.servicenames import Permissions, Roles

from zope.app.interfaces.security import IPermissionService
from zope.app.interfaces.security import IRoleService

from zope.app.security.registries.permissionregistry \
        import permissionRegistry as pregistry
from zope.app.security.registries.roleregistry \
        import roleRegistry as rregistry
from zope.app.security.grants.rolepermission \
        import rolePermissionManager as manager
from zope.app.security.settings \
        import Allow, Deny, Unset
from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class Test(CleanUp, unittest.TestCase):

    def setUp(self):
        CleanUp.setUp(self)

        services.defineService(Permissions, IPermissionService)
        services.provideService(Permissions, pregistry)

        services.defineService(Roles, IRoleService)
        services.provideService(Roles, rregistry)

    def testUnboundRolePermission(self):
        permission = pregistry.definePermission('APerm', 'aPerm title').getId()
        role = rregistry.defineRole('ARole', 'A Role').getId()
        self.assertEqual(manager.getRolesForPermission(permission), [])
        self.assertEqual(manager.getPermissionsForRole(role), [])

    def testRolePermission(self):
        permission = pregistry.definePermission('APerm', 'aPerm title').getId()
        role = rregistry.defineRole('ARole', 'A Role').getId()
        manager.grantPermissionToRole(permission, role)
        self.assertEqual(manager.getRolesForPermission(permission),
                                                        [(role,Allow)])
        self.assertEqual(manager.getPermissionsForRole(role),
                                                    [(permission,Allow)])

    def testManyPermissionsOneRole(self):
        perm1 = pregistry.definePermission('Perm One', 'P1').getId()
        perm2 = pregistry.definePermission('Perm Two', 'P2').getId()
        perm3 = pregistry.definePermission('Perm Three', 'P3').getId()
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        perms = manager.getPermissionsForRole(role1)
        self.assertEqual(len(perms), 0)
        manager.grantPermissionToRole(perm1, role1)
        manager.grantPermissionToRole(perm2, role1)
        manager.grantPermissionToRole(perm2, role1)
        manager.denyPermissionToRole(perm3, role1)
        perms = manager.getPermissionsForRole(role1)
        self.assertEqual(len(perms), 3)
        self.failUnless((perm1,Allow) in perms)
        self.failUnless((perm2,Allow) in perms)
        self.failUnless((perm3,Deny) in perms)
        manager.unsetPermissionFromRole(perm1, role1)
        perms = manager.getPermissionsForRole(role1)
        self.assertEqual(len(perms), 2)
        self.failUnless((perm2,Allow) in perms)

    def testManyRolesOnePermission(self):
        perm1 = pregistry.definePermission('Perm One', 'title').getId()
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        role2 = rregistry.defineRole('Role Two', 'Role #2').getId()
        roles = manager.getRolesForPermission(perm1)
        self.assertEqual(len(roles), 0)
        manager.grantPermissionToRole(perm1, role1)
        manager.grantPermissionToRole(perm1, role2)
        manager.grantPermissionToRole(perm1, role2)
        manager.denyPermissionToRole(perm1, role1)
        roles = manager.getRolesForPermission(perm1)
        self.assertEqual(len(roles), 2)
        self.failIf((role1,Allow) in roles)
        self.failUnless((role1,Deny) in roles)
        self.failUnless((role2,Allow) in roles)
        manager.unsetPermissionFromRole(perm1, role1)
        roles = manager.getRolesForPermission(perm1)
        self.assertEqual(len(roles), 1)
        self.failUnless((role2,Allow) in roles)

    def test_invalidRole(self):
        self.assertRaises(ValueError,
                          manager.grantPermissionToRole, 'perm1', 'role1'
                          )
        perm1 = pregistry.definePermission('Perm One', 'title').getId()
        self.assertRaises(ValueError,
                          manager.grantPermissionToRole, perm1, 'role1'
                          )

    def test_invalidPerm(self):
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        self.assertRaises(ValueError,
                          manager.grantPermissionToRole, 'perm1', role1
                          )
        

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
