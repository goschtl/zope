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
"""Test handler for PrincipalRoleManager module.

$Id: test_principalrolemanager.py,v 1.1 2004/02/27 12:46:33 philikon Exp $
"""
import unittest

from zope.component.service import serviceManager as services
from zope.testing.cleanup import CleanUp

from zope.app.interfaces.security import IAuthenticationService
from zope.app.services.servicenames import Authentication

from zope.app.security.settings import Allow, Deny
from zope.app.security.registries.principalregistry \
     import principalRegistry as pregistry
from zope.app.securitypolicy.roleregistry \
     import roleRegistry as rregistry

from zope.app.securitypolicy.interfaces import IRoleService
from zope.app.securitypolicy.principalrole import principalRoleManager

class Test(CleanUp, unittest.TestCase):

    def setUp(self):
        CleanUp.setUp(self)

        services.defineService('Roles', IRoleService)
        services.provideService('Roles', rregistry)

        services.defineService(Authentication, IAuthenticationService)
        services.provideService(Authentication, pregistry)

    def _make_principal(self, id=None, title=None):
        p = pregistry.definePrincipal(
            id or 'APrincipal',
            title or 'A Principal',
            login = id or 'APrincipal')
        return p.getId()

    def testUnboundPrincipalRole(self):
        role = rregistry.defineRole('ARole', 'A Role').getId()
        principal = self._make_principal()
        self.assertEqual(principalRoleManager.getPrincipalsForRole(role), [])
        self.assertEqual(principalRoleManager.getRolesForPrincipal(principal),
                         [])

    def testPrincipalRoleAllow(self):
        role = rregistry.defineRole('ARole', 'A Role').getId()
        principal = self._make_principal()
        principalRoleManager.assignRoleToPrincipal(role, principal)
        self.assertEqual(principalRoleManager.getPrincipalsForRole(role),
                         [(principal, Allow)])
        self.assertEqual(principalRoleManager.getRolesForPrincipal(principal),
                         [(role, Allow)])

    def testPrincipalRoleDeny(self):
        role = rregistry.defineRole('ARole', 'A Role').getId()
        principal = self._make_principal()
        principalRoleManager.removeRoleFromPrincipal(role, principal)
        self.assertEqual(principalRoleManager.getPrincipalsForRole(role),
                         [(principal, Deny)])
        self.assertEqual(principalRoleManager.getRolesForPrincipal(principal),
                         [(role, Deny)])

    def testPrincipalRoleUnset(self):
        role = rregistry.defineRole('ARole', 'A Role').getId()
        principal = self._make_principal()
        principalRoleManager.removeRoleFromPrincipal(role, principal)
        principalRoleManager.unsetRoleForPrincipal(role, principal)
        self.assertEqual(principalRoleManager.getPrincipalsForRole(role),
                         [])
        self.assertEqual(principalRoleManager.getRolesForPrincipal(principal),
                         [])


    def test_invalidPrincipal(self):
        self.assertRaises(ValueError,
                          principalRoleManager.assignRoleToPrincipal,
                          'role1', 'prin1')
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        self.assertRaises(ValueError,
                          principalRoleManager.assignRoleToPrincipal,
                          role1, 'prin1')

    def test_invalidRole(self):
        prin1 = self._make_principal()
        self.assertRaises(ValueError,
                          principalRoleManager.assignRoleToPrincipal,
                          'role1', prin1)
        

    def testManyRolesOnePrincipal(self):
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        role2 = rregistry.defineRole('Role Two', 'Role #2').getId()
        prin1 = self._make_principal()
        principalRoleManager.assignRoleToPrincipal(role1, prin1)
        principalRoleManager.assignRoleToPrincipal(role2, prin1)
        roles = principalRoleManager.getRolesForPrincipal(prin1)
        self.assertEqual(len(roles), 2)
        self.failUnless((role1, Allow) in roles)
        self.failUnless((role2, Allow) in roles)

    def testManyPrincipalsOneRole(self):
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        prin1 = self._make_principal()
        prin2 = self._make_principal('Principal 2', 'Principal Two')
        principalRoleManager.assignRoleToPrincipal(role1, prin1)
        principalRoleManager.assignRoleToPrincipal(role1, prin2)
        principals = principalRoleManager.getPrincipalsForRole(role1)
        self.assertEqual(len(principals), 2)
        self.failUnless((prin1, Allow) in principals)
        self.failUnless((prin2, Allow) in principals)

    def testPrincipalsAndRoles(self):
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        role2 = rregistry.defineRole('Role Two', 'Role #2').getId()
        prin1 = self._make_principal()
        prin2 = self._make_principal('Principal 2', 'Principal Two')
        principalRoleManager.assignRoleToPrincipal(role1, prin1)
        principalRoleManager.assignRoleToPrincipal(role1, prin2)
        principalRoleManager.assignRoleToPrincipal(role2, prin1)
        principalsAndRoles = principalRoleManager.getPrincipalsAndRoles()
        self.assertEqual(len(principalsAndRoles), 3)
        self.failUnless((role1, prin1, Allow) in principalsAndRoles)
        self.failUnless((role1, prin2, Allow) in principalsAndRoles)
        self.failUnless((role2, prin1, Allow) in principalsAndRoles)

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
