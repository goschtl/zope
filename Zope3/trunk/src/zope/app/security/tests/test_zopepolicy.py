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


Revision information: $Id: test_zopepolicy.py,v 1.12 2003/06/02 16:55:49 jim Exp $
"""

import unittest

from zope.component.service import serviceManager as services

from zope.app.interfaces.security import IPermissionService
from zope.app.interfaces.security import IRoleService
from zope.app.interfaces.security import IAuthenticationService

from zope.app.context import ContextWrapper
from zope.component import getService
from zope.app.services.servicenames import Roles, Permissions, Adapters
from zope.app.services.servicenames import Authentication
from zope.app.interfaces.security import IRolePermissionManager
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.app.security.registries.principalregistry import principalRegistry
from zope.app.security.registries.principalregistry import PrincipalBase
from zope.app.security.registries.roleregistry import roleRegistry
from zope.app.security.grants.principalpermission \
     import principalPermissionManager
from zope.app.security.grants.rolepermission import rolePermissionManager
from zope.app.security.grants.principalrole import principalRoleManager
from zope.app.security.grants.principalpermission \
    import AnnotationPrincipalPermissionManager
from zope.app.interfaces.security import IPrincipalPermissionManager
from zope.app.security.grants.principalrole \
     import AnnotationPrincipalRoleManager
from zope.app.security.grants.rolepermission \
    import AnnotationRolePermissionManager
from zope.app.interfaces.security import IPrincipalRoleManager
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.annotation import IAnnotations
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.services.tests.placefulsetup\
           import PlacefulSetup
from zope.app.security.zopepolicy import permissionsOfPrincipal

class Context:
    def __init__(self, user, stack=[]):
        self.user, self.stack = user, stack

class Unprotected:
    pass

class Principal(PrincipalBase):
    pass


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)


        services.defineService(Permissions, IPermissionService)
        services.provideService(Permissions, permissionRegistry)

        services.defineService(Roles, IRoleService)
        services.provideService(Roles, roleRegistry)

        services.defineService(Authentication, IAuthenticationService)
        services.provideService(Authentication, principalRegistry)



        getService(None,Adapters).provideAdapter(
                       IAttributeAnnotatable, IAnnotations,
                       AttributeAnnotations)

        # set up some principals
        self.jim = principalRegistry.definePrincipal('jim', 'Jim', 'Jim Fulton',
                                                     'jim', '123')

        self.tim = principalRegistry.definePrincipal('tim', 'Tim', 'Tim Peters',
                                                     'tim', '456')

        self.unknown = principalRegistry.defineDefaultPrincipal('unknown',
                    'Unknown', 'Nothing is known about this principal')

        # set up some permissions
        read = permissionRegistry.definePermission('read', 'Read',
                                                   'Read something')
        self.read = read.getId()
        write = permissionRegistry.definePermission('write', 'Write',
                                                    'Write something')
        self.write = write.getId()
        create = permissionRegistry.definePermission('create', 'Create',
                                                     'Create something')
        self.create = create.getId()
        update = permissionRegistry.definePermission('update', 'Update',
                                                     'Update something')
        self.update = update.getId()

        # ... and some roles...
        peon = roleRegistry.defineRole('Peon', 'Site Peon')
        self.peon = peon.getId()

        manager = roleRegistry.defineRole('Manager', 'Site Manager')
        self.manager = manager.getId()

        arole = roleRegistry.defineRole('Another', 'Another Role')
        self.arole = arole.getId()

        # grant and deny some permissions to a principal
        principalPermissionManager.grantPermissionToPrincipal(self.create,
                                                              self.jim.getId())
        principalPermissionManager.denyPermissionToPrincipal(self.update,
                                                             self.jim.getId())

        # grant and deny some permissions to the roles
        rolePermissionManager.grantPermissionToRole(self.read, self.peon)

        rolePermissionManager.grantPermissionToRole(self.read, self.manager)
        rolePermissionManager.grantPermissionToRole(self.write, self.manager)

        # ... and assign roles to principals
        principalRoleManager.assignRoleToPrincipal(self.peon, self.jim.getId())
        principalRoleManager.assignRoleToPrincipal(self.manager, self.tim.getId())

        self.policy = self._makePolicy()

    def _makePolicy(self):

        from zope.app.security.zopepolicy import ZopeSecurityPolicy
        return ZopeSecurityPolicy()

    def __assertPermissions(self, user, expected, object=None):
        permissions = list(permissionsOfPrincipal(user, object))
        permissions.sort()
        self.assertEqual(permissions, expected)

    def testImport(self):
        from zope.app.security.zopepolicy import ZopeSecurityPolicy

    def testGlobalCheckPermission(self):
        self.failUnless(
            self.policy.checkPermission(self.read, None, Context(self.jim)))
        self.failUnless(
            self.policy.checkPermission(self.read, None, Context(self.tim)))
        self.failUnless(
            self.policy.checkPermission(self.write, None, Context(self.tim)))

        self.failIf(self.policy.checkPermission(
            self.read, None, Context(self.unknown)))
        self.failIf(self.policy.checkPermission(
            self.write, None, Context(self.unknown)))

        self.failIf(
            self.policy.checkPermission(
            self.read, None, Context(self.unknown)))

        self.__assertPermissions(self.jim, ['create', 'read'])
        self.__assertPermissions(self.tim, ['read', 'write'])
        self.__assertPermissions(self.unknown, [])

        rolePermissionManager.grantPermissionToRole(self.read, 'Anonymous')

        self.failUnless(
            self.policy.checkPermission(
            self.read, None, Context(self.unknown)))

        self.__assertPermissions(self.unknown, ['read'])

        principalPermissionManager.grantPermissionToPrincipal(
            self.write, self.jim.getId())
        self.failUnless(
            self.policy.checkPermission(self.write, None, Context(self.jim)))

        self.__assertPermissions(self.jim, ['create', 'read', 'write'])

    def testPlayfulPrincipalRole(self):
        getService(None,Adapters).provideAdapter(
            ITest,
            IPrincipalRoleManager, AnnotationPrincipalRoleManager)

        ob1 = TestClass()
        ob2 = TestClass()
        ob3 = TestClass()
        ob  = ContextWrapper(ob3, ContextWrapper(ob2, ob1))
        self.failIf(self.policy.checkPermission(
            self.write, ob, Context(self.jim)))
        AnnotationPrincipalRoleManager(ob).assignRoleToPrincipal(
            self.manager, self.jim.getId())
        self.failUnless(self.policy.checkPermission(
            self.write, ob, Context(self.jim)))


    def testPlayfulRolePermissions(self):

        ARPM = AnnotationRolePermissionManager
        getService(None,Adapters).provideAdapter(ITest,
                            IRolePermissionManager, ARPM)
        test = permissionRegistry.definePermission('test', 'Test', '')
        test = test.getId()

        ob1 = TestClass()
        ob2 = TestClass()
        ob3 = TestClass()

        ob  = ContextWrapper(ob3, ContextWrapper(ob2, ob1))

        self.failIf(self.policy.checkPermission(test, ob, Context(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'write'], ob)

        ARPM(ob2).grantPermissionToRole(test, self.manager)
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'test', 'write'], ob)

        self.failIf(self.policy.checkPermission(test, ob, Context(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read'], ob)


        ARPM(ob3).grantPermissionToRole(test, self.peon)
        self.failUnless(self.policy.checkPermission(
            test, ob, Context(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read', 'test'], ob)



        principalPermissionManager.denyPermissionToPrincipal(
            test, self.jim.getId())
        self.failIf(self.policy.checkPermission(
            test, ob, Context(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read'], ob)

        principalPermissionManager.unsetPermissionForPrincipal(
            test, self.jim.getId())

        # Make sure multiple conflicting role permissions resolve correctly
        ARPM(ob2).grantPermissionToRole(test, 'Anonymous')
        ARPM(ob2).grantPermissionToRole(test, self.arole)
        ARPM(ob3).denyPermissionToRole(test, self.peon)

        new = principalRegistry.definePrincipal('new', 'Newbie',
                                                'Newbie User', 'new', '098')
        principalRoleManager.assignRoleToPrincipal(self.arole, new.getId())
        self.failUnless(self.policy.checkPermission(test, ob, Context(new)))
        self.__assertPermissions(new, ['test'], ob)

        principalRoleManager.assignRoleToPrincipal(self.peon, new.getId())
        self.failIf(self.policy.checkPermission(test, ob, Context(new)))
        self.__assertPermissions(new, ['read'], ob)

    def testPlayfulPrinciplePermissions(self):
        APPM = AnnotationPrincipalPermissionManager
        getService(None,Adapters).provideAdapter(ITest,
                       IPrincipalPermissionManager, APPM)

        ob1 = TestClass()
        ob2 = TestClass()
        ob3 = TestClass()

        test = permissionRegistry.definePermission('test', 'Test', '')
        test = test.getId()

        ob  = ContextWrapper(ob3, ContextWrapper(ob2, ob1))
        self.failIf(self.policy.checkPermission(test, ob, Context(self.tim)))

        self.__assertPermissions(self.tim, ['read', 'write'], ob)

        APPM(ob2).grantPermissionToPrincipal(test, self.tim.getId())
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'test', 'write'], ob)

        APPM(ob3).denyPermissionToPrincipal(test, self.tim.getId())
        self.failIf(self.policy.checkPermission(test, ob,
                                                Context(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'write'], ob)

        APPM(ob1).denyPermissionToPrincipal(test, self.jim.getId())
        APPM(ob3).grantPermissionToPrincipal(test, self.jim.getId())
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read', 'test'], ob)


        APPM(ob3).unsetPermissionForPrincipal(test, self.jim.getId())
        self.failIf(self.policy.checkPermission(test, ob,
                                                Context(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read'], ob)

        # make sure placeless principal permissions override placeful ones
        APPM(ob).grantPermissionToPrincipal(test, self.tim.getId())
        principalPermissionManager.denyPermissionToPrincipal(
            test, self.tim.getId())
        self.failIf(self.policy.checkPermission(test, ob,
                                                Context(self.tim)))

        self.__assertPermissions(self.tim, ['read', 'write'], ob)


class ITest(IAttributeAnnotatable):
    pass

class TestClass:
    __implements__ = ITest

    def __init__(self):
        self._roles       = { 'test' : {} }
        self._permissions = { 'Manager' : {} , 'Peon' : {} }

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
