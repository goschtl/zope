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


Revision information: $Id: testZSP.py,v 1.3 2002/06/20 15:55:03 jim Exp $
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
        jim = principalRegistry.definePrincipal('jim', 'Jim', 'Jim Fulton',
                                                'jim', '123')
        self.jim = jim.getId()
        
        tim = principalRegistry.definePrincipal('tim', 'Tim', 'Tim Peters',
                                                'tim', '456')
        self.tim = tim.getId()

        unknown = principalRegistry.defineDefaultPrincipal(
            'unknown', 'Unknown', 'Nothing is known about this principal')
        self.unknown = unknown.getId()
        
        read = permissionRegistry.definePermission(
            'read', 'Read', 'Read something')
        self.read = read.getId()
        write = permissionRegistry.definePermission(
            'write', 'Write', 'Write something')
        self.write = write.getId()

        peon = roleRegistry.defineRole('Peon', 'Site Peon')
        self.peon = peon.getId()

        manager = roleRegistry.defineRole('Manager', 'Site Manager')
        self.manager = manager.getId()
        
        arole = roleRegistry.defineRole('Another', 'Another Role')
        self.arole = arole.getId()

        rolePermissionManager.grantPermissionToRole(self.read, self.peon)
        
        rolePermissionManager.grantPermissionToRole(self.read, self.manager)
        rolePermissionManager.grantPermissionToRole(self.write, self.manager)

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

        rolePermissionManager.grantPermissionToRole(self.read, 'Anonymous')
        
        self.failUnless(
            self.policy.checkPermission(
            self.read, None, Context(self.unknown)))

        principalPermissionManager.grantPermissionToPrincipal(
            self.write, self.jim)
        self.failUnless(
            self.policy.checkPermission(self.write, None, Context(self.jim)))

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
        ARPM(ob2).grantPermissionToRole(test, self.manager)
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.tim)))

        self.failIf(self.policy.checkPermission(test, ob, Context(self.jim)))
        ARPM(ob3).grantPermissionToRole(test, self.peon)
        self.failUnless(self.policy.checkPermission(
            test, ob, Context(self.jim)))
        # Make sure global principal permissions override placeful role perms
        principalPermissionManager.denyPermissionToPrincipal(
            test, self.jim)
        self.failIf(self.policy.checkPermission(
            test, ob, Context(self.jim)))
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
        principalRoleManager.assignRoleToPrincipal(self.peon, new)
        self.failIf(self.policy.checkPermission(test, ob, Context(new)))
                    
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
        APPM(ob2).grantPermissionToPrincipal(test, self.tim)
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.tim)))
        APPM(ob3).denyPermissionToPrincipal(test, self.tim)
        self.failIf(self.policy.checkPermission(test, ob,
                                                Context(self.tim)))
        APPM(ob1).denyPermissionToPrincipal(test, self.jim)
        APPM(ob3).grantPermissionToPrincipal(test, self.jim)
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.jim)))
        APPM(ob3).unsetPermissionForPrincipal(test, self.jim)
        self.failIf(self.policy.checkPermission(test, ob,
                                                Context(self.jim)))
        # make sure placeful principal permissions override global ones
        APPM(ob).grantPermissionToPrincipal(test, self.tim)
        principalPermissionManager.denyPermissionToPrincipal(
            test, self.tim)
        self.failUnless(self.policy.checkPermission(test, ob,
                                                    Context(self.tim)))
        principalPermissionManager.unsetPermissionForPrincipal(
            test, self.tim)


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
