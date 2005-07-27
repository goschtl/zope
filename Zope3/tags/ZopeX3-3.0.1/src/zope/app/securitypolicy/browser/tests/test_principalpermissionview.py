##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Principal Permission View Tests

$Id$
"""
import unittest

from zope.interface import implements

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.site.interfaces import ISimpleService
from zope.app.annotation.interfaces import IAttributeAnnotatable, IAnnotations
from zope.app.security.interfaces import IAuthenticationService, IPrincipal
from zope.app.security.interfaces import IPermission
from zope.app.servicenames import Authentication
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.security.settings import Allow, Deny, Unset
from zope.app.site.tests.placefulsetup import PlacefulSetup

from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.app.securitypolicy.interfaces import IPrincipalPermissionMap
from zope.app.securitypolicy.browser.principalpermissionview \
     import PrincipalPermissionView

class DummyContext(object):
    implements(IAttributeAnnotatable)


class DummyAuthenticationService(object):
    implements(IAuthenticationService, ISimpleService)

    def __init__(self, principals):
        pr = {}
        for principal in principals:
            pr[principal.id] = principal
        self.principals = pr

    def getPrincipal(self, principal_id):
        return self.principals[principal_id]


class DummyPrincipal(object):
    implements(IPrincipal)

    def __init__(self, id, title):
        self.id = id
        self.title = title


class DummyAdapter(object):
    implements(IPrincipalPermissionManager, IPrincipalPermissionMap)

    def __init__(self, context):
        self._context = context
        if not hasattr(self._context,'principals'):
            self._context.principals = {}

    def grantPermissionToPrincipal(self, permission, principal):
        if not (principal in self._context.principals):
            self._context.principals[principal]={}

        self._context.principals[principal][permission]=Allow

    def denyPermissionToPrincipal(self, permission, principal):
        if not (principal in self._context.principals):
            self._context.principals[principal]={}

        self._context.principals[principal][permission]=Deny

    def unsetPermissionForPrincipal(self, permission, principal):
        if not (principal in self._context.principals):
            return
        try:
            del self._context.principals[principal][permission]
        except KeyError:
            pass

    def getSetting(self, permission, principal):
        try:
            setting =  self._context.principals[principal][permission]

        except KeyError:
            setting = Unset

        return setting

    def getPrincipalsForPermission(self, permission):
        ret = []
        for principal, permissions in self._context.principals.items():
            if permissions in permissions:
                ret.append((principal, permissions[permission]))
        return ret

    def getPermissionsForPrincipal(self, principal):
        try:
            return self._context.principals[principal].items()
        except KeyError:
            return []

class DummyPermission(object):
    implements(IPermission)
    
    def __init__(self, id, title):
        self.id = id
        self.title = title


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        sm = zapi.getGlobalServices()
        self._permissions = []
        self._permissions.append(DummyPermission('qux', 'Qux'))
        self._permissions.append(DummyPermission('baz', 'Baz'))
        
        for perm in self._permissions:
            ztapi.provideUtility(IPermission, perm, perm.id)

        sm.defineService(Authentication, IAuthenticationService)

        self._principals = []
        self._principals.append(DummyPrincipal('foo', 'Foo'))
        self._principals.append(DummyPrincipal('bar', 'Bar'))

        sm.provideService(Authentication,
            DummyAuthenticationService(principals = self._principals))
        ztapi.provideAdapter(IAttributeAnnotatable,
                       IPrincipalPermissionManager, DummyAdapter)
        ztapi.provideAdapter(
            IAttributeAnnotatable, IAnnotations, AttributeAnnotations)

    def _makeOne(self):
        return PrincipalPermissionView(DummyContext(), None)

    def testGrantPermissions(self):
        view = self._makeOne()
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        denied_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Deny')

        self.assertEqual(len(allowed_perms), 0, 'List not empty')
        self.assertEqual(len(denied_perms), 0, 'List not empty')
        view.grantPermissions(self._principals[0].id,
                              [self._permissions[0].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Allow'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Deny'),
                         [])

        view.grantPermissions(self._principals[0].id,
                              [self._permissions[1].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Allow').sort(),
                         self._permissions.sort())
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Deny'),
                         [])

        view.grantPermissions(self._principals[1].id,
                              [self._permissions[0].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].id,'Allow'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].id,'Deny'),
                         [])

        view.grantPermissions(self._principals[1].id,
                              [self._permissions[1].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].id,'Allow').sort(),
                         self._permissions.sort())
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].id,'Deny'),
                         [])

    def testDenyPermissions(self):
        view = self._makeOne()
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        denied_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Deny')

        self.assertEqual(len(allowed_perms), 0, 'List not empty')
        self.assertEqual(len(denied_perms), 0, 'List not empty')
        view.denyPermissions(self._principals[0].id,
                             [self._permissions[0].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Deny'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Allow'),
                         [])

        view.denyPermissions(self._principals[0].id,
                             [self._permissions[1].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Deny').sort(),
                         self._permissions.sort())
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Allow'),
                         [])

        view.denyPermissions(self._principals[1].id, [
            self._permissions[0].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].id,'Deny'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].id,'Allow'),
                         [])

        view.denyPermissions(self._principals[1].id,
                             [self._permissions[1].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].id,'Deny').sort(),
                         self._permissions.sort())
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].id,'Allow'),
                         [])

    def testAllowDenyPermissions(self):
        view = self._makeOne()
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        denied_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Deny')

        self.assertEqual(len(allowed_perms), 0, 'List not empty')
        self.assertEqual(len(denied_perms), 0, 'List not empty')

        view.grantPermissions(self._principals[0].id,
                              [self._permissions[0].id])

        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Allow'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Deny'),
                         [])

        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        self.assertEqual(len(allowed_perms), 1, 'List has wrong length')

        # Now change it to deny
        view.denyPermissions(self._principals[0].id,
                             [self._permissions[0].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Deny'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Allow'),
                         [])

        view.grantPermissions(self._principals[0].id,
                              [self._permissions[1].id])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Deny'),  [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].id,'Allow'), [self._permissions[1]])

    def testUnsetPermissions(self):
        view = self._makeOne()

        view.grantPermissions(self._principals[0].id,
                              [self._permissions[0].id])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        self.assertEqual(len(allowed_perms), 1, 'List has wrong length')

        view.unsetPermissions(self._principals[0].id,
                              [self._permissions[0].id])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        self.assertEqual(len(allowed_perms), 0, 'Permission not unset')

        # Deleting mutiple in one step
        view.grantPermissions(self._principals[0].id,
                              [self._permissions[0].id,
                               self._permissions[1].id])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        self.assertEqual(len(allowed_perms), 2, 'List has wrong length')

        view.unsetPermissions(self._principals[0].id,
                              [self._permissions[0].id,
                               self._permissions[1].id])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        self.assertEqual(len(allowed_perms), 0, 'Some permissions not unset')

        # Deleting in a row
        view.grantPermissions(self._principals[0].id,
                              [self._permissions[0].id,
                               self._permissions[1].id])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        self.assertEqual(len(allowed_perms), 2, 'List has wrong length')

        view.unsetPermissions(self._principals[0].id,
                              [self._permissions[0].id])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        self.assertEqual(len(allowed_perms), 1, 'Some permissions not unset')

        view.unsetPermissions(self._principals[0].id,
                              [self._permissions[1].id])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].id, 'Allow')
        self.assertEqual(len(allowed_perms), 0, 'Not all permissions unset')

        # Ask for another way of getting the unset permisssions
        unset_perms = view.getUnsetPermissionsForPrincipal(
            self._principals[0].id)
        # the permissions include zope.Public
        self.assertEqual(len(unset_perms), 3, 'Not all permissions unset')

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
