import os, sys
import glob

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase
from Testing.ZopeTestCase.functional import Functional
from AccessControl import Unauthorized

# we need to install FiveTest *before* Five as Five processes zcml
# in all the products it can find.
ZopeTestCase.installProduct('FiveTest')
ZopeTestCase.installProduct('Five')

from zope.app.form.browser.submit import Update

class EditFormTestCase(Functional, ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        self.folder.manage_addProduct['FiveTest'].manage_addFieldSimpleContent(
            'edittest', 'Test')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        
    def test_editform(self):
        response = self.publish('/test_folder_1_/edittest/edit.html',
                                basic='manager:r00t')
        # we're using a GET request to post variables, but seems to be
        # the easiest..
        response = self.publish(
            '/test_folder_1_/edittest/edit.html?%s=1&field.title=FooTitle&field.description=FooDescription' % Update,
            basic='manager:r00t')
        self.assertEquals('FooTitle', self.folder.edittest.title)
        self.assertEquals('FooDescription', self.folder.edittest.description)

    def test_editform_invalid(self):
        # missing title, which is required
        self.folder.edittest.description = ''
        
        response = self.publish(
            '/test_folder_1_/edittest/edit.html?%s=1&field.title=&field.description=BarDescription' % Update,
            basic='manager:r00t')
        # we expect that we get a 200 Ok
        self.assertEqual(200, response.getStatus())
        self.assertEquals('Test', self.folder.edittest.title)
        self.assertEquals('', self.folder.edittest.description)
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EditFormTestCase))
    return suite

if __name__ == '__main__':
    framework()
