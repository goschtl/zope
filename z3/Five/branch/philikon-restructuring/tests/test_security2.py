
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing.ZopeTestCase import ZopeTestCase, FunctionalTestCase, installProduct

installProduct("Five")
installProduct("PythonScripts")

from AccessControl import getSecurityManager

import glob
from Products.Five.tests.products import FiveTest
_prefix = os.path.dirname(FiveTest.__file__)
dir_resource_names = [os.path.basename(r)
                      for r in (glob.glob('%s/*.png' % _prefix) +
                                glob.glob('%s/*.pt' % _prefix) +
                                glob.glob('%s/[a-z]*.py' % _prefix) +
                                glob.glob('%s/*.css' % _prefix))]

ViewManagementScreens = 'View management screens'

from Products.Five.tests.products.FiveTest.simplecontent import manage_addSimpleContent
from Products.Five.tests.helpers import RestrictedPythonTestCase

class PublishTest(FunctionalTestCase):
    """A functional test for security actually involving the publisher.
    """
    def afterSetUp(self):
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    def test_no_permission(self):
        for view_name in view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name,
                                    basic='viewer:secret')
            # we expect that we get a 401 Unauthorized
            self.assertEqual(response.getStatus(), 401)

    def test_all_permissions(self):
        permissions = self.folder.possible_permissions()
        self.folder._addRole('Viewer')
        self.folder.manage_role('Viewer', permissions)
        self.folder.manage_addLocalRoles('viewer', ['Viewer'])
        
        for view_name in view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name,
                                    basic='viewer:secret')
            self.assertEqual(response.getStatus(), 200)

    def test_almost_all_permissions(self):
        permissions = self.folder.possible_permissions()
        permissions.remove(ViewManagementScreens)
        self.folder._addRole('Viewer')
        self.folder.manage_role('Viewer', permissions)
        self.folder.manage_addLocalRoles('viewer', ['Viewer'])
        
        for view_name in view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name,
                                    basic='viewer:secret')
            # we expect that we get a 401 Unauthorized
            self.assertEqual(response.getStatus(), 401)

    def test_manager_permission(self):
        for view_name in view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name,
                                    basic='manager:r00t')
            # we expect that we get a 200 Ok
            self.assertEqual(response.getStatus(), 200)

    def test_public_permission(self):
        for view_name in public_view_names:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name)
            self.assertEqual(response.getStatus(), 200)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(SecurityTest))
    suite.addTest(makeSuite(PublishTest))
    return suite

if __name__ == '__main__':
    framework()
