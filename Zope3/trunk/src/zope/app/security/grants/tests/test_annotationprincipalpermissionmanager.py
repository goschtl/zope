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
"""Test handler for AnnotationPrincipalPermissionManager module."""

import sys
import unittest

from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.component import getService
from zope.component.servicenames import Adapters
from zope.app.interfaces.annotation import IAnnotations
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.security.registries.permissionregistry \
    import permissionRegistry as permregistry
from zope.app.security.registries.principalregistry \
    import principalRegistry as prinregistry
from zope.app.security.grants.principalpermission \
    import AnnotationPrincipalPermissionManager
from zope.app.security.settings import Allow, Deny, Unset
from zope.app.tests.placelesssetup import PlacelessSetup

class Manageable:
    __implements__ = IAttributeAnnotatable

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        getService(None,Adapters).provideAdapter(
            IAttributeAnnotatable, IAnnotations,
            AttributeAnnotations)

    def _make_principal(self, id=None, title=None):
        p = prinregistry.definePrincipal(
            id or 'APrincipal',
            title or 'A Principal',
            login = id or 'APrincipal')
        return p.getId()

    def testUnboundPrincipalPermission(self):
        manager = AnnotationPrincipalPermissionManager(Manageable())
        permission = permregistry.definePermission('APerm', 'title')
        permission = permission.getId()
        principal = self._make_principal()
        self.assertEqual(manager.getPrincipalsForPermission(permission), [])
        self.assertEqual(manager.getPermissionsForPrincipal(principal), [])

    def testPrincipalPermission(self):
        manager = AnnotationPrincipalPermissionManager(Manageable())
        permission = permregistry.definePermission('APerm', 'title')
        permission = permission.getId()
        principal = self._make_principal()

        # check that an allow permission is saved correctly
        manager.grantPermissionToPrincipal(permission, principal)
        self.assertEqual(manager.getPrincipalsForPermission(permission),
                         [(principal, Allow)])
        self.assertEqual(manager.getPermissionsForPrincipal(principal),
                         [(permission, Allow)])

        # check that the allow permission is removed.
        manager.unsetPermissionForPrincipal(permission, principal)
        self.assertEqual(manager.getPrincipalsForPermission(permission), [])
        self.assertEqual(manager.getPermissionsForPrincipal(principal), [])

        # now put a deny in there, check it's set.
        manager.denyPermissionToPrincipal(permission, principal)
        self.assertEqual(manager.getPrincipalsForPermission(permission),
                         [(principal, Deny)])
        self.assertEqual(manager.getPermissionsForPrincipal(principal),
                         [(permission, Deny)])

        # test for deny followed by allow . The latter should override.
        manager.grantPermissionToPrincipal(permission, principal)
        self.assertEqual(manager.getPrincipalsForPermission(permission),
                         [(principal, Allow)])
        self.assertEqual(manager.getPermissionsForPrincipal(principal),
                         [(permission, Allow)])

        # check that allow followed by allow is just a single allow.
        manager.grantPermissionToPrincipal(permission, principal)
        self.assertEqual(manager.getPrincipalsForPermission(permission),
                         [(principal, Allow)])
        self.assertEqual(manager.getPermissionsForPrincipal(principal),
                         [(permission, Allow)])

        # check that two unsets in a row quietly ignores the second one.
        manager.unsetPermissionForPrincipal(permission, principal)
        manager.unsetPermissionForPrincipal(permission, principal)
        self.assertEqual(manager.getPrincipalsForPermission(permission), [])
        self.assertEqual(manager.getPermissionsForPrincipal(principal), [])

        # check the result of getSetting() when it's empty.
        self.assertEqual(manager.getSetting(permission, principal), Unset)

        # check the result of getSetting() when it's allowed.
        manager.grantPermissionToPrincipal(permission, principal)
        self.assertEqual(manager.getSetting(permission, principal), Allow)

        # check the result of getSetting() when it's denied.
        manager.denyPermissionToPrincipal(permission, principal)
        self.assertEqual(manager.getSetting(permission, principal), Deny)

    def testManyPermissionsOnePrincipal(self):
        manager = AnnotationPrincipalPermissionManager(Manageable())
        perm1 = permregistry.definePermission('Perm One', 'title').getId()
        perm2 = permregistry.definePermission('Perm Two', 'title').getId()
        prin1 = self._make_principal()
        manager.grantPermissionToPrincipal(perm1, prin1)
        manager.grantPermissionToPrincipal(perm2, prin1)
        perms = manager.getPermissionsForPrincipal(prin1)
        self.assertEqual(len(perms), 2)
        self.failUnless((perm1,Allow) in perms)
        self.failUnless((perm2,Allow) in perms)
        manager.denyPermissionToPrincipal(perm2, prin1)
        perms = manager.getPermissionsForPrincipal(prin1)
        self.assertEqual(len(perms), 2)
        self.failUnless((perm1,Allow) in perms)
        self.failUnless((perm2,Deny) in perms)

    def testManyPrincipalsOnePermission(self):
        manager = AnnotationPrincipalPermissionManager(Manageable())
        perm1 = permregistry.definePermission('Perm One', 'title').getId()
        prin1 = self._make_principal()
        prin2 = self._make_principal('Principal 2', 'Principal Two')
        manager.grantPermissionToPrincipal(perm1, prin1)
        manager.denyPermissionToPrincipal(perm1, prin2)
        principals = manager.getPrincipalsForPermission(perm1)
        self.assertEqual(len(principals), 2)
        self.failUnless((prin1,Allow) in principals)
        self.failUnless((prin2,Deny) in principals)

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
