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

Revision information:
$Id: testRoleService.py,v 1.6 2002/07/16 23:41:15 jim Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
    import PlacefulSetup
from Zope.ComponentArchitecture import getServiceManager, getService
from Zope.App.OFS.Services.ServiceManager.ServiceDirective \
     import ServiceDirective
from Zope.App.Traversing import getPhysicalPathString

from Zope.App.Traversing.Traverser import Traverser
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.App.Traversing.DefaultTraversable import DefaultTraversable
from Zope.App.Traversing.ITraversable import ITraversable


from Zope.App.Traversing.IPhysicallyLocatable import IPhysicallyLocatable
from Zope.App.Traversing.IContainmentRoot import IContainmentRoot
from Zope.App.Traversing.PhysicalLocationAdapters \
     import WrapperPhysicallyLocatable, RootPhysicallyLocatable


from Zope.App.OFS.Container.ContainerTraversable import ContainerTraversable
from Zope.App.OFS.Container.IContainer import ISimpleReadContainer



class RoleServiceTests(PlacefulSetup, TestCase):

    def _Test__new(self):
        return RoleService()

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()

        # set up traversal services
        adapterService=getService(None, "Adapters")
        adapterService.provideAdapter(
            None, ITraverser, Traverser)
        adapterService.provideAdapter(
            None, ITraversable, DefaultTraversable)
        adapterService.provideAdapter(
            ISimpleReadContainer, ITraversable, ContainerTraversable)


        adapterService.provideAdapter(
              None, IPhysicallyLocatable, WrapperPhysicallyLocatable)
        adapterService.provideAdapter(
              IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)



        from Zope.App.Security.IRoleService import IRoleService
        from Zope.App.Security.Registries.RoleRegistry import roleRegistry
        sm=getServiceManager(None)
        defineService=sm.defineService
        provideService=sm.provideService
        defineService("Roles", IRoleService)
        self.roleRegistry=roleRegistry
        provideService("Roles", self.roleRegistry)
        self.createServiceManager()
        
        self.sm=getServiceManager(self.rootFolder)
        from Zope.App.OFS.Services.RoleService.RoleService import RoleService
        self.rs = RoleService()
        self.sm.Packages['default'].setObject("myRoleService", self.rs)

        path = "%s/Packages/default/myRoleService" % getPhysicalPathString(
            self.sm)
        directive = ServiceDirective("Roles", path)
        self.sm.Packages['default'].setObject("myRoleServiceDir", directive)
        self.sm.bindService(directive)

        self.rs=getService(self.rootFolder,"Roles")

    def testGetRole(self):
        self.roleRegistry.defineRole('Manager', 'Manager', '')
        
        from Zope.App.OFS.Services.RoleService.Role import Role
        r = Role("Hacker","","")
        self.rs.setObject("Hacker", r)
        self.assertEqual(self.rs.getRole('Hacker').getId(), 'Hacker')
        self.assertEqual(self.rs.getRole('Manager').getId(), 'Manager')

        roles = [role.getId() for role in self.rs.getRoles()]
        roles.sort()

        self.assertEqual(roles, ['Anonymous', 'Hacker', 'Manager'])
    
    def testGetRoleFromLayeredServices(self):
        self.roleRegistry.defineRole('Manager', 'Manager', '')
        
        from Zope.App.OFS.Services.RoleService.Role import Role
        r = Role("Hacker","","")
        self.rs.setObject("Hacker", r)
        self.createServiceManager(self.folder1)
        self.sm1=getServiceManager(self.folder1)
        from Zope.App.OFS.Services.RoleService.RoleService import RoleService
        self.rs1 = RoleService()

        self.sm1.Packages['default'].setObject("myRoleService", self.rs1)

        path = "%s/Packages/default/myRoleService" % getPhysicalPathString(
            self.sm1)
        directive = ServiceDirective("Roles", path)
        self.sm1.Packages['default'].setObject("myRoleServiceDir", directive)
        self.sm1.bindService(directive)

        self.rs1=self.sm1.getService("Roles")
        r1=Role("Reviewer",'','')
        self.rs1.setObject("Reviewer", r1)
        self.assertEqual(self.rs1.getRole('Hacker').getId(), 'Hacker')
        self.assertEqual(self.rs1.getRole('Manager').getId(), 'Manager')
        self.assertEqual(self.rs1.getRole('Reviewer').getId(), 'Reviewer')

        roles = [role.getId() for role in self.rs1.getRoles()]
        roles.sort()

        self.assertEqual(roles, ['Anonymous', 'Hacker', 'Manager','Reviewer'])
        

        
def test_suite():
    loader=TestLoader()
    return loader.loadTestsFromTestCase(RoleServiceTests)

if __name__=='__main__':
    TextTestRunner().run(test_suite())
