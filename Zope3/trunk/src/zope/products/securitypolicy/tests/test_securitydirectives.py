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
"""Security Directives Tests

$Id: test_securitydirectives.py,v 1.2 2004/01/14 22:55:35 chrism Exp $
"""
import unittest

from zope.component.service import serviceManager as services
from zope.app.services.servicenames import Permissions, Authentication
from zope.app.interfaces.security import IPermissionService
from zope.products.securitypolicy.interfaces import IRoleService
from zope.app.interfaces.security import IAuthenticationService

from zope.configuration.config import ConfigurationConflictError
from zope.configuration import xmlconfig

from zope.testing.cleanup import CleanUp # Base class w registry cleanup

import zope.products.securitypolicy.tests
import zope.products.securitypolicy.tests
from zope.app.security.settings import Allow
from zope.app.security.registries.principalregistry import principalRegistry
from zope.app.security.registries.permissionregistry \
        import permissionRegistry as pregistry
from zope.products.securitypolicy.roleregistry import roleRegistry as rregistry
from zope.products.securitypolicy.rolepermission \
        import rolePermissionManager as role_perm_mgr
from zope.products.securitypolicy.principalpermission \
    import principalPermissionManager as principal_perm_mgr
from zope.products.securitypolicy.principalrole \
    import principalRoleManager as principal_role_mgr


class TestBase(CleanUp):

    def setUp(self):
        CleanUp.setUp(self)
    
        services.defineService(Permissions, IPermissionService)
        services.provideService(Permissions, pregistry)
    
        services.defineService("Roles", IRoleService)
        services.provideService("Roles", rregistry)
    
        services.defineService(Authentication, IAuthenticationService)
        services.provideService(Authentication, principalRegistry)


class TestRoleDirective(TestBase, unittest.TestCase):

    def testRegister(self):
        context = xmlconfig.file("role.zcml",
                                 zope.products.securitypolicy.tests)

        role = rregistry.getRole("zope.Everyperson")
        self.failUnless(role.getId().endswith('Everyperson'))
        self.assertEqual(role.getTitle(), 'Tout le monde')
        self.assertEqual(role.getDescription(),
                         'The common man, woman, person, or thing')

    def testDuplicationRegistration(self):
        self.assertRaises(ConfigurationConflictError, xmlconfig.file,
                          "role_duplicate.zcml",
                          zope.products.securitypolicy.tests)


class TestSecurityMapping(TestBase, unittest.TestCase):

    def setUp(self):
        TestBase.setUp(self)
        pregistry.definePermission("zope.Foo", '', '')
        rregistry.defineRole("zope.Bar", '', '')
        principalRegistry.definePrincipal("zope.Blah", '', '')
        self.context = xmlconfig.file("mapping.zcml",
                                      zope.products.securitypolicy.tests)

    def test_PermRoleMap(self):
        roles = role_perm_mgr.getRolesForPermission("zope.Foo")
        perms = role_perm_mgr.getPermissionsForRole("zope.Bar")

        self.assertEqual(len(roles), 1)
        self.failUnless(("zope.Bar",Allow) in roles)

        self.assertEqual(len(perms), 1)
        self.failUnless(("zope.Foo",Allow) in perms)

    def test_PermPrincipalMap(self):
        principals = principal_perm_mgr.getPrincipalsForPermission("zope.Foo")
        perms = principal_perm_mgr.getPermissionsForPrincipal("zope.Blah")

        self.assertEqual(len(principals), 1)
        self.failUnless(("zope.Blah", Allow) in principals)

        self.assertEqual(len(perms), 1)
        self.failUnless(("zope.Foo", Allow) in perms)

    def test_RolePrincipalMap(self):
        principals = principal_role_mgr.getPrincipalsForRole("zope.Bar")
        roles = principal_role_mgr.getRolesForPrincipal("zope.Blah")

        self.assertEqual(len(principals), 1)
        self.failUnless(("zope.Blah", Allow) in principals)

        self.assertEqual(len(roles), 1)
        self.failUnless(("zope.Bar", Allow) in roles)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestRoleDirective),
        unittest.makeSuite(TestSecurityMapping),
        ))

if __name__ == '__main__':
    unittest.main()
