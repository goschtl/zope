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
"""

$Id: testPrincipalPermissionView.py,v 1.1 2002/06/20 15:55:01 jim Exp $
"""

import unittest

from Zope.ComponentArchitecture import getService, getServiceManager
from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations
from Zope.App.Security.IPermissionService import IPermissionService
from Zope.App.Security.IAuthenticationService import IAuthenticationService
from Zope.App.Security.IPrincipalPermissionManager \
        import IPrincipalPermissionManager
from Zope.App.Security.IPrincipalPermissionMap import IPrincipalPermissionMap
from Zope.App.Security.Settings import Allow, Deny, Unset
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup

class DummyContext:

    __implements__ = IAttributeAnnotatable
#IPrincipalPermissionManager, IPrincipalPermissionMap

class DummyPermissionService:

    __implements__ = IPermissionService

    def __init__(self, perm_objs):
        perms = {}
        for perm_obj in perm_objs:
            perms[perm_obj.getId()] = perm_obj
            
        self.perms = perms

    def getPermission(self,pr_id):
        return self.perms[pr_id]

    def getPermissions(self):
        return self.perms.keys()
    

class DummyAuthenticationService:
    __implements__ = IAuthenticationService
    
    def __init__(self, principals):
        pr = {}
        for principal in principals:
            pr[principal.getId()] = principal
        self.principals = pr

    def getPrincipal(self, principal_id):
        return self.principals[principal_id]
    
class DummyAdapter:

    __implements__ = IPrincipalPermissionManager, IPrincipalPermissionMap
    
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
        
class DummyObject:
    def __init__(self, id, title):
        self._id = id
        self._title = title

    def getId(self):
        return self._id

    def getTitle(self):
        return self._title


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self._permissions = []
        self._permissions.append(DummyObject('qux', 'Qux'))
        self._permissions.append(DummyObject('baz', 'Baz'))
        defineService=getServiceManager(None).defineService
        provideService=getServiceManager(None).provideService

        defineService(
                 'PermissionService', IPermissionService)
        provideService('PermissionService',
                 DummyPermissionService(self._permissions))

        defineService('AuthenticationService',
                 IAuthenticationService)

        self._principals = []
        self._principals.append(DummyObject('foo', 'Foo'))
        self._principals.append(DummyObject('bar', 'Bar'))

        provideService('AuthenticationService',
            DummyAuthenticationService(principals = self._principals))
        provideAdapter=getService(None,'Adapters').provideAdapter
        provideAdapter(IAttributeAnnotatable,
                       IPrincipalPermissionManager, DummyAdapter)
        provideAdapter(
            IAttributeAnnotatable, IAnnotations, AttributeAnnotations)

    def _makeOne(self):
        from Zope.App.Security.Grants.Views.Browser.PrincipalPermissionView \
             import PrincipalPermissionView
        return PrincipalPermissionView(DummyContext(), None)

    def testGrantPermissions(self):
        view = self._makeOne()
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        denied_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Deny')
        
        self.assertEqual(len(allowed_perms), 0, 'List not empty')
        self.assertEqual(len(denied_perms), 0, 'List not empty')
        view.grantPermissions(self._principals[0].getId(),
                              [self._permissions[0].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Allow'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Deny'),
                         [])

        view.grantPermissions(self._principals[0].getId(),
                              [self._permissions[1].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Allow').sort(),
                         self._permissions.sort())
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Deny'),
                         [])

        view.grantPermissions(self._principals[1].getId(),
                              [self._permissions[0].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].getId(),'Allow'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].getId(),'Deny'),
                         [])

        view.grantPermissions(self._principals[1].getId(),
                              [self._permissions[1].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].getId(),'Allow').sort(),
                         self._permissions.sort())
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].getId(),'Deny'),
                         [])

    def testDenyPermissions(self):
        view = self._makeOne()
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        denied_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Deny')
        
        self.assertEqual(len(allowed_perms), 0, 'List not empty')
        self.assertEqual(len(denied_perms), 0, 'List not empty')
        view.denyPermissions(self._principals[0].getId(),
                             [self._permissions[0].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Deny'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Allow'),
                         [])

        view.denyPermissions(self._principals[0].getId(),
                             [self._permissions[1].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Deny').sort(),
                         self._permissions.sort())
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Allow'),
                         [])

        view.denyPermissions(self._principals[1].getId(), [
            self._permissions[0].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].getId(),'Deny'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].getId(),'Allow'),
                         [])

        view.denyPermissions(self._principals[1].getId(),
                             [self._permissions[1].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].getId(),'Deny').sort(),
                         self._permissions.sort())
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[1].getId(),'Allow'),
                         [])

    def testAllowDenyPermissions(self):
        view = self._makeOne()
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        denied_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Deny')
        
        self.assertEqual(len(allowed_perms), 0, 'List not empty')
        self.assertEqual(len(denied_perms), 0, 'List not empty')

        view.grantPermissions(self._principals[0].getId(),
                              [self._permissions[0].getId()])

        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Allow'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Deny'),
                         [])

        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        self.assertEqual(len(allowed_perms), 1, 'List has wrong length')

        # Now change it to deny
        view.denyPermissions(self._principals[0].getId(),
                             [self._permissions[0].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Deny'),
                         [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Allow'),
                         [])
        
        view.grantPermissions(self._principals[0].getId(),
                              [self._permissions[1].getId()])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Deny'),  [self._permissions[0]])
        self.assertEqual(view.getPermissionsForPrincipal(
            self._principals[0].getId(),'Allow'), [self._permissions[1]])

    def testUnsetPermissions(self):
        view = self._makeOne()

        view.grantPermissions(self._principals[0].getId(),
                              [self._permissions[0].getId()])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        self.assertEqual(len(allowed_perms), 1, 'List has wrong length')

        view.unsetPermissions(self._principals[0].getId(),
                              [self._permissions[0].getId()])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        self.assertEqual(len(allowed_perms), 0, 'Permission not unset')

        # Deleting mutiple in one step
        view.grantPermissions(self._principals[0].getId(),
                              [self._permissions[0].getId(),
                               self._permissions[1].getId()])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        self.assertEqual(len(allowed_perms), 2, 'List has wrong length')

        view.unsetPermissions(self._principals[0].getId(),
                              [self._permissions[0].getId(),
                               self._permissions[1].getId()])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        self.assertEqual(len(allowed_perms), 0, 'Some permissions not unset')

        # Deleting in a row
        view.grantPermissions(self._principals[0].getId(),
                              [self._permissions[0].getId(),
                               self._permissions[1].getId()])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        self.assertEqual(len(allowed_perms), 2, 'List has wrong length')

        view.unsetPermissions(self._principals[0].getId(),
                              [self._permissions[0].getId()])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        self.assertEqual(len(allowed_perms), 1, 'Some permissions not unset')

        view.unsetPermissions(self._principals[0].getId(),
                              [self._permissions[1].getId()])
        allowed_perms = view.getPermissionsForPrincipal(
            self._principals[0].getId(), 'Allow')
        self.assertEqual(len(allowed_perms), 0, 'Not all permissions unset')

        # Ask for an other way of getting the unset permisssions
        unset_perms = view.getUnsetPermissionsForPrincipal(
            self._principals[0].getId())
        self.assertEqual(len(unset_perms), 2, 'Not all permissions unset')
        
def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
