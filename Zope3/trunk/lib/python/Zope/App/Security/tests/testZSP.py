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


Revision information: $Id: testZSP.py,v 1.6 2002/11/08 18:35:06 stevea Exp $
"""


import unittest

from Interface import Interface
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.ComponentArchitecture import getService
from Zope.App.Security.IRolePermissionManager import IRolePermissionManager
from Zope.App.Security.Registries.PermissionRegistry import permissionRegistry 
from Zope.App.Security.Registries.PrincipalRegistry import principalRegistry 
from Zope.App.Security.Registries.RoleRegistry import roleRegistry
from Zope.App.Security.Grants.Global.PrincipalPermissionManager \
     import principalPermissionManager 
from Zope.App.Security.Grants.Global.RolePermissionManager \
     import rolePermissionManager 
from Zope.App.Security.Grants.Global.PrincipalRoleManager \
     import principalRoleManager 
from Zope.App.Security.Grants.AnnotationPrincipalPermissionManager \
    import AnnotationPrincipalPermissionManager 
from Zope.App.Security.Grants.Global.PrincipalPermissionManager \
    import PrincipalPermissionManager 
from Zope.App.Security.IPrincipalPermissionManager \
    import IPrincipalPermissionManager 
from Zope.App.Security.Grants.AnnotationPrincipalRoleManager \
    import AnnotationPrincipalRoleManager 
from Zope.App.Security.Grants.Global.PrincipalRoleManager \
    import PrincipalRoleManager 
from Zope.App.Security.Grants.AnnotationRolePermissionManager \
    import AnnotationRolePermissionManager 
from Zope.App.Security.IPrincipalRoleManager import IPrincipalRoleManager 
from Zope.Exceptions import Unauthorized, Forbidden
from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup\
           import PlacefulSetup
from Zope.App.Security.ZopeSecurityPolicy import permissionsOfPrincipal

class Context:
    def __init__(self, user, stack=[]):
        self.user, self.stack = user, stack
    
class Unprotected:
    pass



class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        getService(None,"Adapters").provideAdapter(
                       IAttributeAnnotatable, IAnnotations,
                       AttributeAnnotations)    

        # set up some principals
        jim = principalRegistry.definePrincipal('jim', 'Jim', 'Jim Fulton',
                                                'jim', '123')
        self.jim = jim.getId()
        
        tim = principalRegistry.definePrincipal('tim', 'Tim', 'Tim Peters',
                                                'tim', '456')
        self.tim = tim.getId()

        unknown = principalRegistry.defineDefaultPrincipal('unknown', 
                    'Unknown', 'Nothing is known about this principal')
        self.unknown = unknown.getId()
        
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
        self.update = update

        # ... and some roles...
        peon = roleRegistry.defineRole('Peon', 'Site Peon')
        self.peon = peon.getId()

        manager = roleRegistry.defineRole('Manager', 'Site Manager')
        self.manager = manager.getId()
        
        arole = roleRegistry.defineRole('Another', 'Another Role')
        self.arole = arole.getId()

        # grant and deny some permissions to a principal
        principalPermissionManager.grantPermissionToPrincipal(self.create, self.jim)
        principalPermissionManager.denyPermissionToPrincipal(self.update, self.jim)
        
        # grant and deny some permissions to the roles
        rolePermissionManager.grantPermissionToRole(self.read, self.peon)

        rolePermissionManager.grantPermissionToRole(self.read, self.manager)
        rolePermissionManager.grantPermissionToRole(self.write, self.manager)

        # ... and assign roles to principals
        principalRoleManager.assignRoleToPrincipal(self.peon, self.jim)
        principalRoleManager.assignRoleToPrincipal(self.manager, self.tim)

        self.policy = self._makePolicy()

    def _makePolicy( self ):

        from Zope.App.Security.ZopeSecurityPolicy import ZopeSecurityPolicy
        return ZopeSecurityPolicy()

    def testImport( self ):

        from Zope.App.Security.ZopeSecurityPolicy import ZopeSecurityPolicy

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
            self.write, self.jim)
        self.failUnless(
            self.policy.checkPermission(self.write, None, Context(self.jim)))

        self.__assertPermissions(self.jim, ['create', 'read', 'write'])

    def __assertPermissions(self, user, expected, object=None):
        permissions = list(permissionsOfPrincipal(user, object))
        permissions.sort()
        self.assertEqual(permissions, expected)
        

    def testPlayfulPrincipalRole(self):
        getService(None,"Adapters").provideAdapter(
            ITest,
            IPrincipalRoleManager, AnnotationPrincipalRoleManager)

        ob1 = TestClass()
        ob2 = TestClass()
        ob3 = TestClass()
        ob  = ContextWrapper(ob3, ContextWrapper(ob2, ob1))
        self.failIf(self.policy.checkPermission(
            self.write, ob, Context(self.jim)))
        AnnotationPrincipalRoleManager(ob).assignRoleToPrincipal(
            self.manager, self.jim)
        self.failUnless(self.policy.checkPermission(
            self.write, ob, Context(self.jim)))
        

    def testPlayfulRolePermissions(self):
        
        ARPM = AnnotationRolePermissionManager
        getService(None,"Adapters").provideAdapter(ITest,
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
            test, self.jim)
        self.failIf(self.policy.checkPermission(
            test, ob, Context(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read'], ob)

        principalPermissionManager.unsetPermissionForPrincipal(
            test, self.jim)

        # Make sure multiple conflicting role permissions resolve correctly
        ARPM(ob2).grantPermissionToRole(test, 'Anonymous')
        ARPM(ob2).grantPermissionToRole(test, self.arole)
        ARPM(ob3).denyPermissionToRole(test, self.peon)
        
        new = principalRegistry.definePrincipal('new', 'Newbie', 
                                                'Newbie User', 'new', '098')
        new = new.getId()
        principalRoleManager.assignRoleToPrincipal(self.arole, new)
        self.failUnless(self.policy.checkPermission(test, ob, Context(new)))
        self.__assertPermissions(new, ['test'], ob)

        principalRoleManager.assignRoleToPrincipal(self.peon, new)
        self.failIf(self.policy.checkPermission(test, ob, Context(new)))
        self.__assertPermissions(new, ['read'], ob)
                    
    def testPlayfulPrinciplePermissions(self):
        APPM = AnnotationPrincipalPermissionManager
        getService(None,"Adapters").provideAdapter(ITest,
                       IPrincipalPermissionManager, APPM)

        ob1 = TestClass()
        ob2 = TestClass()
        ob3 = TestClass()

        test = permissionRegistry.definePermission('test', 'Test', '')
        test = test.getId()

        ob  = ContextWrapper(ob3, ContextWrapper(ob2, ob1))
        self.failIf(self.policy.checkPermission(test, ob, Context(self.tim)))

        self.__assertPermissions(self.tim, ['read', 'write'], ob)

        APPM(ob2).grantPermissionToPrincipal(test, self.tim)
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'test', 'write'], ob)

        APPM(ob3).denyPermissionToPrincipal(test, self.tim)
        self.failIf(self.policy.checkPermission(test, ob,
                                                Context(self.tim)))
        self.__assertPermissions(self.tim, ['read', 'write'], ob)

        APPM(ob1).denyPermissionToPrincipal(test, self.jim)
        APPM(ob3).grantPermissionToPrincipal(test, self.jim)
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read', 'test'], ob)


        APPM(ob3).unsetPermissionForPrincipal(test, self.jim)
        self.failIf(self.policy.checkPermission(test, ob,
                                                Context(self.jim)))
        self.__assertPermissions(self.jim, ['create', 'read'], ob)

        # make sure placeless principal permissions override placeful ones
        APPM(ob).grantPermissionToPrincipal(test, self.tim)
        principalPermissionManager.denyPermissionToPrincipal(
            test, self.tim)
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
