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
$Id: testRoleService.py,v 1.2 2002/06/10 23:28:12 jim Exp $
"""
from unittest import TestCase, TestLoader, TextTestRunner
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
    import PlacefulSetup
from Zope.ComponentArchitecture import getServiceManager, getService

class RoleServiceTests(PlacefulSetup, TestCase):

    def _Test__new(self):
        return RoleService()

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        from Zope.App.Security.IRoleService import IRoleService
        from Zope.App.Security.RoleRegistry import roleRegistry
        sm=getServiceManager(None)
        defineService=sm.defineService
        provideService=sm.provideService
        defineService("RoleService", IRoleService)
        self.roleRegistry=roleRegistry
        provideService("RoleService", self.roleRegistry)
        self.createServiceManager()
        self.sm=getServiceManager(self.rootFolder)
        from Zope.App.OFS.Services.RoleService.RoleService import RoleService
        self.rs = RoleService()
        self.sm.setObject("myRoleService", self.rs)
        self.sm.bindService("RoleService","myRoleService")
        self.rs=getService(self.rootFolder,"RoleService")

    def testGetRole(self):
        self.roleRegistry.defineRole('Manager', 'Manager', '')
        
        from Zope.App.OFS.Services.RoleService.Role import Role
        r = Role()
        r.setId("Hacker")
        self.rs.setObject("Hacker", r)
        self.assertEqual(self.rs.getRole('Hacker').getId(), 'Hacker')
        self.assertEqual(self.rs.getRole('Manager').getId(), 'Manager')

        roles = [role.getId() for role in self.rs.getRoles()]
        roles.sort()

        self.assertEqual(roles, ['Anonymous', 'Hacker', 'Manager'])
    
    def testGetRoleFromLayeredServices(self):
        self.roleRegistry.defineRole('Manager', 'Manager', '')
        
        from Zope.App.OFS.Services.RoleService.Role import Role
        r = Role()
        r.setId("Hacker")
        self.rs.setObject("Hacker", r)
        self.createServiceManager(self.folder1)
        self.sm1=getServiceManager(self.folder1)
        from Zope.App.OFS.Services.RoleService.RoleService import RoleService
        self.rs1 = RoleService()
        self.sm1.setObject("myRoleService", self.rs1)
        self.sm1.bindService("RoleService","myRoleService")
        self.rs1=self.sm1.getService("RoleService")
        r1=Role()
        r1.setId("Reviewer")
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
