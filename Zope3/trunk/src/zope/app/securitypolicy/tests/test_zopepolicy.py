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
"""Tests the standard zope policy.

$Id$
"""
import unittest
from zope.interface import implements
from zope.interface.verify import verifyObject

from zope.app import zapi
from zope.app.annotation.attribute import AttributeAnnotations
from zope.app.annotation.interfaces import IAttributeAnnotatable, IAnnotations
from zope.app.security.principalregistry import principalRegistry, PrincipalBase
from zope.app.security.interfaces import IPermission, IAuthenticationService
from zope.app.security.permission import Permission
from zope.app.servicenames import Authentication
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.tests import ztapi

from zope.app.securitypolicy.interfaces import IRole
from zope.app.securitypolicy.interfaces import IRolePermissionManager
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager

from zope.app.securitypolicy.role import Role
from zope.app.securitypolicy.zopepolicy import permissionsOfPrincipal
from zope.app.securitypolicy.principalpermission \
     import principalPermissionManager
from zope.app.securitypolicy.rolepermission import rolePermissionManager
from zope.app.securitypolicy.principalrole import principalRoleManager
from zope.app.securitypolicy.principalpermission \
    import AnnotationPrincipalPermissionManager
from zope.app.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.app.securitypolicy.principalrole \
     import AnnotationPrincipalRoleManager
from zope.app.securitypolicy.rolepermission \
    import AnnotationRolePermissionManager


class RequestStub(object):
    def __init__(self, principal, interaction=None):
        self.principal = principal
        self.interaction = interaction

class Interaction(object):
    def __init__(self, user):
        self.participations = [RequestStub(user, self)]

class Unprotected(object):
    pass

class Principal(PrincipalBase):
    pass


def defineRole(id, title=None, description=None):
    role = Role(id, title, description)
    ztapi.provideUtility(IRole, role, name=role.id)
    return role

def definePermission(id, title=None, description=None):
    perm = Permission(id, title, description)
    ztapi.provideUtility(IPermission, perm, name=perm.id)
    return perm


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        services = zapi.getGlobalServices()

        services.defineService(Authentication, IAuthenticationService)
        services.provideService(Authentication, principalRegistry)

        ztapi.provideAdapter(
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
        self.read = definePermission('read', 'Read', 'Read something').id

        self.write = definePermission('write', 'Write', 'Write something').id

        self.create = definePermission('create', 'Create',
                                       'Create something').id

        self.update = definePermission('update', 'Update',
                                       'Update something').id

        # ... and some roles...
        defineRole("zope.Anonymous", "Everybody",
                   "All users have this role implicitly")

        self.peon = defineRole('Peon', 'Site Peon').id

        self.manager = defineRole('Manager', 'Site Manager').id

        self.arole = defineRole('Another', 'Another Role').id

        # grant and deny some permissions to a principal
        principalPermissionManager.grantPermissionToPrincipal(
            self.create, self.jim.id)
        principalPermissionManager.denyPermissionToPrincipal(
            self.update, self.jim.id)

        # grant and deny some permissions to the roles
        rolePermissionManager.grantPermissionToRole(self.read, self.peon)

        rolePermissionManager.grantPermissionToRole(self.read, self.manager)
        rolePermissionManager.grantPermissionToRole(self.write, self.manager)

        # ... and assign roles to principals
        principalRoleManager.assignRoleToPrincipal(self.peon, self.jim.id)
        principalRoleManager.assignRoleToPrincipal(self.manager, self.tim.id)

        self.policy = self._makePolicy()


    def _makePolicy(self):
        from zope.app.securitypolicy.zopepolicy import ZopeSecurityPolicy
        return ZopeSecurityPolicy()


    def __assertPermissions(self, user, expected, object=None):
        permissions = list(permissionsOfPrincipal(user, object))
        permissions.sort()
        self.assertEqual(permissions, expected)

    def testImport(self):
        from zope.app.securitypolicy.zopepolicy import ZopeSecurityPolicy

    def testInterfaces(self):
        from zope.security.interfaces import ISecurityPolicy
        from zope.app.securitypolicy.zopepolicy import ZopeSecurityPolicy
        verifyObject(ISecurityPolicy, ZopeSecurityPolicy())

    def testCreateInteraction(self):
        from zope.security.interfaces import IInteraction
        from zope.app.securitypolicy.zopepolicy import ZopeSecurityPolicy
        i1 = ZopeSecurityPolicy().createInteraction(None)
        verifyObject(IInteraction, i1)
        self.assertEquals(list(i1.participations), [])

        user = object()
        rq = RequestStub(user)
        i2 = ZopeSecurityPolicy().createInteraction(rq)
        verifyObject(IInteraction, i2)
        self.assertEquals(list(i2.participations), [rq])

    def testGlobalCheckPermission(self):
        self.failUnless(
            self.policy.checkPermission(self.read, None, Interaction(self.jim)))
        self.failUnless(
            self.policy.checkPermission(self.read, None, Interaction(self.tim)))
        self.failUnless(
            self.policy.checkPermission(self.write, None, Interaction(self.tim)))

        self.failIf(self.policy.checkPermission(
            self.read, None, Interaction(self.unknown)))
        self.failIf(self.policy.checkPermission(
            self.write, None, Interaction(self.unknown)))

        self.failIf(
            self.policy.checkPermission(
            self.read, None, Interaction(self.unknown)))

        self.__assertPermissions(self.jim, ['create', 'read'])
        self.__assertPermissions(self.tim, ['read', 'write'])
        self.__assertPermissions(self.unknown, [])

        rolePermissionManager.grantPermissionToRole(
            self.read, 'zope.Anonymous')

        self.failUnless(
            self.policy.checkPermission(
            self.read, None, Interaction(self.unknown)))

        self.__assertPermissions(self.unknown, ['read'])

        principalPermissionManager.grantPermissionToPrincipal(
            self.write, self.jim.id)
        self.failUnless(
            self.policy.checkPermission(self.write, None, Interaction(self.jim)))

        self.__assertPermissions(self.jim, ['create', 'read', 'write'])

    def testPlaylessPrincipalRole(self):
        self.failIf(self.policy.checkPermission(
            self.write, None, Interaction(self.jim)))
        principalRoleManager.assignRoleToPrincipal(
            self.manager, self.jim.id)
        self.failUnless(self.policy.checkPermission(
            self.write, None, Interaction(self.jim)))
        principalRoleManager.removeRoleFromPrincipal(
            self.manager, self.jim.id)
        self.failIf(self.policy.checkPermission(
            self.write, None, Interaction(self.jim)))

    def testPlayfulPrincipalRole(self):
        ztapi.provideAdapter(
            ITest,
            IPrincipalRoleManager, AnnotationPrincipalRoleManager)

        ob1 = TestClass()
        ob2 = TestClass(); ob2.__parent__ = ob1
        ob3 = TestClass(); ob3.__parent__ = ob2

        self.failIf(self.policy.checkPermission(
            self.write, ob3, Interaction(self.jim)))
        AnnotationPrincipalRoleManager(ob3).assignRoleToPrincipal(
            self.manager, self.jim.id)
        self.failUnless(self.policy.checkPermission(
            self.write, ob3, Interaction(self.jim)))
        AnnotationPrincipalRoleManager(ob3).removeRoleFromPrincipal(
            self.manager, self.jim.id)
        self.failIf(self.policy.checkPermission(
            self.write, ob3, Interaction(self.jim)))

    def testPlayfulRolePermissions(self):

        ARPM = AnnotationRolePermissionManager
        ztapi.provideAdapter(ITest,
                            IRolePermissionManager, ARPM)
        test = definePermission('test', 'Test', '')
        test = test.id

        ob1 = TestClass()
        ob2 = TestClass(); ob2.__parent__ = ob1
        ob3 = TestClass(); ob3.__parent__ = ob2

        self.failIf(self.policy.checkPermission(test, ob3, Interaction(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'write'], ob3)

        ARPM(ob2).grantPermissionToRole(test, self.manager)
        self.failUnless(self.policy.checkPermission(test, ob3,
                                                    Interaction(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'test', 'write'], ob3)

        self.failIf(self.policy.checkPermission(test, ob3, Interaction(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read'], ob3)


        ARPM(ob3).grantPermissionToRole(test, self.peon)
        self.failUnless(self.policy.checkPermission(
            test, ob3, Interaction(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read', 'test'], ob3)



        principalPermissionManager.denyPermissionToPrincipal(
            test, self.jim.id)
        self.failIf(self.policy.checkPermission(
            test, ob3, Interaction(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read'], ob3)

        principalPermissionManager.unsetPermissionForPrincipal(
            test, self.jim.id)

        # Make sure multiple conflicting role permissions resolve correctly
        ARPM(ob2).grantPermissionToRole(test, 'zope.Anonymous')
        ARPM(ob2).grantPermissionToRole(test, self.arole)
        ARPM(ob3).denyPermissionToRole(test, self.peon)

        new = principalRegistry.definePrincipal('new', 'Newbie',
                                                'Newbie User', 'new', '098')
        principalRoleManager.assignRoleToPrincipal(self.arole, new.id)
        self.failUnless(self.policy.checkPermission(test, ob3, Interaction(new)))
        self.__assertPermissions(new, ['test'], ob3)

        principalRoleManager.assignRoleToPrincipal(self.peon, new.id)
        self.failIf(self.policy.checkPermission(test, ob3, Interaction(new)))
        self.__assertPermissions(new, ['read'], ob3)

    def testPlayfulPrinciplePermissions(self):
        APPM = AnnotationPrincipalPermissionManager
        ztapi.provideAdapter(ITest,
                       IPrincipalPermissionManager, APPM)

        ob1 = TestClass()
        ob2 = TestClass(); ob2.__parent__ = ob1
        ob3 = TestClass(); ob3.__parent__ = ob2

        test = definePermission('test', 'Test', '').id

        self.failIf(self.policy.checkPermission(test, ob3, Interaction(self.tim)))

        self.__assertPermissions(self.tim, ['read', 'write'], ob3)

        APPM(ob2).grantPermissionToPrincipal(test, self.tim.id)
        self.failUnless(self.policy.checkPermission(
            test, ob3, Interaction(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'test', 'write'], ob3)

        APPM(ob3).denyPermissionToPrincipal(test, self.tim.id)
        self.failIf(self.policy.checkPermission(
            test, ob3, Interaction(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'write'], ob3)

        APPM(ob1).denyPermissionToPrincipal(test, self.jim.id)
        APPM(ob3).grantPermissionToPrincipal(test, self.jim.id)
        self.failUnless(self.policy.checkPermission(
            test, ob3, Interaction(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read', 'test'], ob3)


        APPM(ob3).unsetPermissionForPrincipal(test, self.jim.id)
        self.failIf(self.policy.checkPermission(
            test, ob3, Interaction(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read'], ob3)

        # make sure placeless principal permissions override placeful ones
        APPM(ob3).grantPermissionToPrincipal(test, self.tim.id)
        principalPermissionManager.denyPermissionToPrincipal(
            test, self.tim.id)
        self.failIf(self.policy.checkPermission(
            test, ob3, Interaction(self.tim)))

        self.__assertPermissions(self.tim, ['read', 'write'], ob3)


class ITest(IAttributeAnnotatable):
    pass

class TestClass(object):
    implements(ITest)

    __parent__ = None

    def __init__(self):
        self._roles       = { 'test' : {} }
        self._permissions = { 'Manager' : {} , 'Peon' : {} }

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
