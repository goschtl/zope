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
"""Test the Role service.

$Id: test_roleservice.py,v 1.6 2003/12/14 08:47:31 srichter Exp $
"""

from unittest import TestCase, TestLoader, TextTestRunner
from zope.app.tests import setup
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component import getServiceManager
from zope.app.interfaces.security import IRoleService
from zope.app.security.registries.roleregistry import roleRegistry
from zope.app.services.role import RoleService
from zope.app.services.role import Role

class RoleServiceTests(PlacefulSetup, TestCase):

    def _Test__new(self):
        return RoleService()

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)

        root_sm = getServiceManager(None)

        root_sm.defineService("Roles", IRoleService)
        self.roleRegistry = roleRegistry
        root_sm.provideService("Roles", roleRegistry)

        self.rs = setup.addService(sm, 'Roles', RoleService())

    def testGetRole(self):
        self.roleRegistry.defineRole('zope.Manager', 'Manager', '')

        r = Role("zope.Hacker","","")
        self.rs["zope.Hacker"] = r
        self.assertEqual(self.rs.getRole('zope.Hacker').getId(), 'zope.Hacker')
        self.assertEqual(self.rs.getRole('zope.Manager').getId(),
                         'zope.Manager')

        roles = [role.getId() for role in self.rs.getRoles()]
        roles.sort()

        self.assertEqual(roles,
                         ['zope.Anonymous', 'zope.Hacker', 'zope.Manager'])

    def testGetRoleFromLayeredServices(self):
        self.roleRegistry.defineRole('zope.Manager', 'Manager', '')

        r = Role("zope.Hacker","","")
        self.rs["zope.Hacker"] = r

        sm1 = self.makeSite('folder1')
        rs1 = setup.addService(sm1, 'Roles', RoleService())

        r1 = Role("zope.Reviewer",'','')
        rs1["zope.Reviewer"] = r1

        self.assertEqual(rs1.getRole('zope.Hacker').getId(), 'zope.Hacker')
        self.assertEqual(rs1.getRole('zope.Manager').getId(), 'zope.Manager')
        self.assertEqual(rs1.getRole('zope.Reviewer').getId(), 'zope.Reviewer')

        roles = [role.getId() for role in rs1.getRoles()]
        roles.sort()

        self.assertEqual(
            roles,
            ['zope.Anonymous', 'zope.Hacker', 'zope.Manager','zope.Reviewer'])



def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(RoleServiceTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
