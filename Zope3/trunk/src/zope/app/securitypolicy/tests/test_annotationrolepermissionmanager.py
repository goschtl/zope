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
"""Test handler for Annotation Role Permission Manager.

$Id: test_annotationrolepermissionmanager.py,v 1.2 2004/03/05 18:39:09 srichter Exp $
"""
import unittest
from zope.interface import implements

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.security import IPermissionService
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.app.security.settings import Allow, Deny
from zope.app.services.servicenames import Permissions, Adapters
from zope.app.services.tests.placefulsetup import PlacefulSetup

from zope.app.securitypolicy.role import Role
from zope.app.securitypolicy.interfaces import IRole
from zope.app.securitypolicy.rolepermission \
     import AnnotationRolePermissionManager

class Manageable:
    implements(IAttributeAnnotatable)

def defineRole(id, title=None, description=None):
    role = Role(id, title, description)
    ztapi.provideUtility(IRole, role, name=role.id)
    return role

class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        defineService = zapi.getServiceManager(None).defineService
        provideService = zapi.getServiceManager(None).provideService
        defineService(Permissions, IPermissionService)
        provideService(Permissions, permissionRegistry)
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)

        read = permissionRegistry.definePermission('read', 'Read Something')
        self.read = read.getId()

        write = permissionRegistry.definePermission('write', 'Write Something')
        self.write = write.getId()

        peon = defineRole('peon', 'Poor Slob')
        self.peon = peon.id

        manager = defineRole('manager', 'Supreme Being')
        self.manager = manager.id

    def testNormal(self):
        obj = Manageable()
        mgr = AnnotationRolePermissionManager(obj)
        mgr.grantPermissionToRole(self.read,self.manager)
        mgr.grantPermissionToRole(self.write,self.manager)
        mgr.grantPermissionToRole(self.write,self.manager)

        mgr.grantPermissionToRole(self.read,self.peon)

        l = list(mgr.getPermissionsForRole(self.manager))
        self.failUnless((self.read, Allow) in l)
        self.failUnless((self.write, Allow) in l)

        l = list(mgr.getPermissionsForRole(self.peon))
        self.failUnless([(self.read, Allow)] == l)

        l = list(mgr.getRolesForPermission(self.read))
        self.failUnless((self.manager, Allow) in l)
        self.failUnless((self.peon, Allow) in l)

        l = list(mgr.getRolesForPermission(self.write))
        self.assertEqual(l, [(self.manager, Allow)])

        mgr.denyPermissionToRole(self.read, self.peon)
        l = list(mgr.getPermissionsForRole(self.peon))
        self.assertEqual(l, [(self.read, Deny)])

        mgr.unsetPermissionFromRole(self.read, self.peon)

        l = list(mgr.getRolesForPermission(self.read))
        self.assertEqual(l, [(self.manager, Allow)])


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
