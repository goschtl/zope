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

$Id: test_securitydirectives.py,v 1.13 2004/01/14 22:55:27 chrism Exp $
"""
import unittest

from zope.component.service import serviceManager as services
from zope.app.services.servicenames import Permissions, Authentication
from zope.app.interfaces.security import IPermissionService
from zope.app.interfaces.security import IAuthenticationService

from zope.configuration.config import ConfigurationConflictError
from zope.configuration import xmlconfig

from zope.testing.cleanup import CleanUp # Base class w registry cleanup

import zope.app.security.tests
from zope.app.security.settings import Allow
from zope.app.security.registries.principalregistry import principalRegistry
from zope.app.security.registries.permissionregistry \
    import permissionRegistry as pregistry

class TestBase(CleanUp):

    def setUp(self):
        CleanUp.setUp(self)

        services.defineService(Permissions, IPermissionService)
        services.provideService(Permissions, pregistry)

        services.defineService(Authentication, IAuthenticationService)
        services.provideService(Authentication, principalRegistry)


class TestPrincipalDirective(TestBase, unittest.TestCase):

    def testRegister(self):
        context = xmlconfig.file("principal.zcml", zope.app.security.tests)
        reg=principalRegistry

        p = reg.getPrincipal('zope.p1')
        self.assertEqual(p.getId(), 'zope.p1')
        self.assertEqual(p.getTitle(), 'Sir Tim Peters')
        self.assertEqual(p.getDescription(), 'Tim Peters')
        p = reg.getPrincipal('zope.p2')
        self.assertEqual(p.getId(), 'zope.p2')
        self.assertEqual(p.getTitle(), 'Sir Jim Fulton')
        self.assertEqual(p.getDescription(), 'Jim Fulton')

        self.assertEqual(len(reg.getPrincipals('')), 2)


class TestPermissionDirective(TestBase, unittest.TestCase):

    def testRegister(self):
        context = xmlconfig.file("perm.zcml", zope.app.security.tests)
        perm = pregistry.getPermission("Can.Do.It")
        self.failUnless(perm.getId().endswith('Can.Do.It'))
        self.assertEqual(perm.getTitle(), 'A Permissive Permission')
        self.assertEqual(perm.getDescription(),
                         'This permission lets you do anything')

    def testDuplicationRegistration(self):
        self.assertRaises(ConfigurationConflictError, xmlconfig.file,
                          "perm_duplicate.zcml", zope.app.security.tests)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestPrincipalDirective),
        unittest.makeSuite(TestPermissionDirective),
        ))

if __name__ == '__main__':
    unittest.main()
