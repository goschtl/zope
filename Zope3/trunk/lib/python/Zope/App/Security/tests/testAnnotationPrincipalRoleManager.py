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
"""Test handler for PrincipalRoleManager module."""

import sys
import unittest

from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.ComponentArchitecture import getService
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations
from Zope.App.Security.RoleRegistry import roleRegistry as rregistry
from Zope.App.Security.PrincipalRegistry import principalRegistry as pregistry
from Zope.App.Security.AnnotationPrincipalRoleManager \
        import AnnotationPrincipalRoleManager
from Zope.App.Security.Settings import Assign, Remove
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup import PlacefulSetup

class Manageable:
    __implements__ = IAttributeAnnotatable

class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        getService(None,"Adapters").provideAdapter(
            IAttributeAnnotatable, IAnnotations,
            AttributeAnnotations)
                       
    def _make_principal(self, id=None, title=None):
        p = pregistry.definePrincipal(
            id or 'APrincipal',
            title or 'A Principal',
            login = id or 'APrincipal')
        return p.getId()

    def testUnboundPrincipalRole(self):
        principalRoleManager = AnnotationPrincipalRoleManager(Manageable())
        role = rregistry.defineRole('ARole', 'A Role').getId()
        principal = self._make_principal()
        self.assertEqual(principalRoleManager.getPrincipalsForRole(role), [])
        self.assertEqual(principalRoleManager.getRolesForPrincipal(principal),
                         [])

    def testPrincipalRoleAssign(self):
        principalRoleManager = AnnotationPrincipalRoleManager(Manageable())
        role = rregistry.defineRole('ARole', 'A Role').getId()
        principal = self._make_principal()
        principalRoleManager.assignRoleToPrincipal(role, principal)
        self.assertEqual(principalRoleManager.getPrincipalsForRole(role),
                         [(principal,Assign)])
        self.assertEqual(principalRoleManager.getRolesForPrincipal(principal),
                         [(role,Assign)])

    def testPrincipalRoleRemove(self):
        principalRoleManager = AnnotationPrincipalRoleManager(Manageable())
        role = rregistry.defineRole('ARole', 'A Role').getId()
        principal = self._make_principal()
        principalRoleManager.removeRoleFromPrincipal(role, principal)
        self.assertEqual(principalRoleManager.getPrincipalsForRole(role),
                         [(principal,Remove)])
        self.assertEqual(principalRoleManager.getRolesForPrincipal(principal),
                         [(role,Remove)])

    def testPrincipalRoleUnset(self):
        principalRoleManager = AnnotationPrincipalRoleManager(Manageable())
        role = rregistry.defineRole('ARole', 'A Role').getId()
        principal = self._make_principal()
        principalRoleManager.removeRoleFromPrincipal(role, principal)
        principalRoleManager.unsetRoleForPrincipal(role, principal)
        self.assertEqual(principalRoleManager.getPrincipalsForRole(role),
                         [])
        self.assertEqual(principalRoleManager.getRolesForPrincipal(principal),
                         [])

    def testManyRolesOnePrincipal(self):
        principalRoleManager = AnnotationPrincipalRoleManager(Manageable())
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        role2 = rregistry.defineRole('Role Two', 'Role #2').getId()
        prin1 = self._make_principal()
        principalRoleManager.assignRoleToPrincipal(role1, prin1)
        principalRoleManager.assignRoleToPrincipal(role2, prin1)
        roles = principalRoleManager.getRolesForPrincipal(prin1)
        self.assertEqual(len(roles), 2)
        self.failUnless((role1,Assign) in roles)
        self.failUnless((role2,Assign) in roles)

    def testManyPrincipalsOneRole(self):
        principalRoleManager = AnnotationPrincipalRoleManager(Manageable())
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        prin1 = self._make_principal()
        prin2 = self._make_principal('Principal 2', 'Principal Two')
        principalRoleManager.assignRoleToPrincipal(role1, prin1)
        principalRoleManager.assignRoleToPrincipal(role1, prin2)
        principals = principalRoleManager.getPrincipalsForRole(role1)
        self.assertEqual(len(principals), 2)
        self.failUnless((prin1,Assign) in principals)
        self.failUnless((prin2,Assign) in principals)

    def testPrincipalsAndRoles(self):
        principalRoleManager = AnnotationPrincipalRoleManager(Manageable())
        principalsAndRoles = principalRoleManager.getPrincipalsAndRoles()
        self.assertEqual(len(principalsAndRoles), 0)
        role1 = rregistry.defineRole('Role One', 'Role #1').getId()
        role2 = rregistry.defineRole('Role Two', 'Role #2').getId()
        prin1 = self._make_principal()
        prin2 = self._make_principal('Principal 2', 'Principal Two')
        principalRoleManager.assignRoleToPrincipal(role1, prin1)
        principalRoleManager.assignRoleToPrincipal(role1, prin2)
        principalRoleManager.assignRoleToPrincipal(role2, prin1)
        principalsAndRoles = principalRoleManager.getPrincipalsAndRoles()
        self.assertEqual(len(principalsAndRoles), 3)
        self.failUnless((role1,prin1,Assign) in principalsAndRoles)
        self.failUnless((role1,prin2,Assign) in principalsAndRoles)
        self.failUnless((role2,prin1,Assign) in principalsAndRoles)


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
