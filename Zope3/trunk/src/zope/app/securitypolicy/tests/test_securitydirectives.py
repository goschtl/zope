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

$Id$
"""
import unittest

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.servicenames import Authentication
from zope.app.security.interfaces import IAuthenticationService

from zope.configuration.config import ConfigurationConflictError
from zope.configuration import xmlconfig
from zope.app.tests.placelesssetup import PlacelessSetup

from zope.app.security.interfaces import IPermission
from zope.app.security.permission import Permission
from zope.app.security.settings import Allow
from zope.app.security.principalregistry import principalRegistry

from zope.app.securitypolicy.role import Role
from zope.app.securitypolicy.interfaces import IRole
from zope.app.securitypolicy.rolepermission \
        import rolePermissionManager as role_perm_mgr
from zope.app.securitypolicy.principalpermission \
    import principalPermissionManager as principal_perm_mgr
from zope.app.securitypolicy.principalrole \
    import principalRoleManager as principal_role_mgr
import zope.app.securitypolicy.tests


def defineRole(id, title=None, description=None):
    role = Role(id, title, description)
    ztapi.provideUtility(IRole, role, name=role.id)
    return role


class TestBase(PlacelessSetup):

    def setUp(self):
        super(TestBase, self).setUp()
        services = zapi.getGlobalServices()

        services.defineService(Authentication, IAuthenticationService)
        services.provideService(Authentication, principalRegistry)


class TestRoleDirective(TestBase, unittest.TestCase):

    def testRegister(self):
        context = xmlconfig.file("role.zcml",
                                 zope.app.securitypolicy.tests)

        role = zapi.getUtility(IRole, "zope.Everyperson")
        self.failUnless(role.id.endswith('Everyperson'))
        self.assertEqual(role.title, 'Tout le monde')
        self.assertEqual(role.description,
                         'The common man, woman, person, or thing')

    def testDuplicationRegistration(self):
        self.assertRaises(ConfigurationConflictError, xmlconfig.file,
                          "role_duplicate.zcml",
                          zope.app.securitypolicy.tests)


class TestSecurityMapping(TestBase, unittest.TestCase):

    def setUp(self):
        super(TestSecurityMapping, self).setUp()
        ztapi.provideUtility(IPermission, Permission('zope.Foo', ''),
                             name='zope.Foo')
        defineRole("zope.Bar", '', '')
        principalRegistry.definePrincipal("zope.Blah", '', '')
        self.context = xmlconfig.file("mapping.zcml",
                                      zope.app.securitypolicy.tests)

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
