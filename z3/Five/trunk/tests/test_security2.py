import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from AccessControl import getSecurityManager
from Testing import ZopeTestCase

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('FiveTest')

ViewManagementScreens = 'View management screens'

class SecurityTestCase(ZopeTestCase.ZopeTestCase):
    
    def afterSetUp(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    def assertPermission(self, permission, object):
         user = getSecurityManager().getUser()
         self.assert_(user.has_permission(permission, object))

    def assertNoPermission(self, permission, object):
         user = getSecurityManager().getUser()
         self.assert_(not user.has_permission(permission, object))
        
    def test_one(self):
        self.login('viewer')
        view = self.folder.unrestrictedTraverse('testoid/eagle.txt')
        self.assertNoPermission(ViewManagementScreens, view)
        
    def test_two(self):
        self.login('manager')
        view = self.folder.unrestrictedTraverse('testoid/eagle.txt')
        self.assertPermission(ViewManagementScreens, view)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityTestCase))
    return suite

if __name__ == '__main__':
    framework()

