import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from AccessControl import getSecurityManager
from Testing import ZopeTestCase
from AccessControl import Unauthorized

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('FiveTest')
ZopeTestCase.installProduct('PythonScripts')

ViewManagementScreens = 'View management screens'

class RestrictedPythonTest(ZopeTestCase.ZopeTestCase):
    """
    Test whether code is really restricted
    
    Kind permission from Plone to use this.
    """

    def addPS(self, id, params='', body=''):
        # clean up any 'ps' that's already here..
        try:
            self.folder._getOb('ps')
            self.folder.manage_delObjects(['ps'])
        except AttributeError:
            pass # it's okay, no 'ps' exists yet
        factory = self.folder.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript(id)
        self.folder[id].ZPythonScript_edit(params, body)

    def check(self, psbody):
        self.addPS('ps', body=psbody)
        try: 
            self.folder.ps()
        except (ImportError, Unauthorized), e:
            self.fail(e)

    def checkUnauthorized(self, psbody):
        self.addPS('ps', body=psbody)
        try:
            self.folder.ps()
        except (AttributeError, Unauthorized):
            pass
        
class SecurityTestCase(RestrictedPythonTest):
    
    def afterSetUp(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    view_names = [
        'eagle.txt',
        'falcon.html',
        'owl.html',
        'flamingo.html',
        'flamingo2.html',
        'condor.html']
    
    def test_no_permission(self):
        self.login('viewer')
        for view_name in self.view_names:
            self.checkUnauthorized(
                'context.restrictedTraverse("testoid/%s")()' % view_name)

    def test_permission(self):
        self.login('manager')
        for view_name in self.view_names:
            self.check(
                'context.restrictedTraverse("testoid/%s")()' % view_name)
        
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SecurityTestCase))
    return suite

if __name__ == '__main__':
    framework()

