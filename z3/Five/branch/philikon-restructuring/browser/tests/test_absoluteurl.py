##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test AbsoluteURL

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

from zope.interface import directlyProvides
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.browser.interfaces import IAbsoluteURL
from Products.Five.tests.helpers import manage_addFiveTraversableFolder

class AbsoluteURLTests(ZopeTestCase):

    def afterSetUp(self):
	manage_addFiveTraversableFolder(self.folder, 'testoid', 'Testoid')

    def test_breadcrumbs(self):
        view = self.folder.unrestrictedTraverse('testoid/@@absolute_url')
        expected = (
            {'url': 'http://nohost', 'name': ''},
            {'url': 'http://nohost/test_folder_1_', 'name': 'test_folder_1_'},
            {'url': 'http://nohost/test_folder_1_/testoid', 'name': 'testoid'})
        self.assertEquals(expected, view.breadcrumbs())

    def test_virtualhost_breadcrumbs(self):
        # Get REQUEST in shape
        request = self.request = self.app.REQUEST
        request['PARENTS'] = [self.folder.test_folder_1_]
        request.setServerURL(
            protocol='http', hostname='foo.bar.com', port='80')
        request.setVirtualRoot('')

        view = self.folder.unrestrictedTraverse('testoid/@@absolute_url')
        expected = (
            {'url': 'http://foo.bar.com', 'name': 'test_folder_1_'},
            {'url': 'http://foo.bar.com/testoid', 'name': 'testoid'})
        self.assertEquals(expected, view.breadcrumbs())

    def test_containement_root_breadcrumbs(self):
        # Should stop breadcrumbs from crumbing
        directlyProvides(self.folder, IContainmentRoot)
        view = self.folder.unrestrictedTraverse('testoid/@@absolute_url')
        expected = (
            {'url': 'http://nohost/test_folder_1_', 'name': 'test_folder_1_'},
            {'url': 'http://nohost/test_folder_1_/testoid', 'name': 'testoid'})
        self.assertEquals(expected, view.breadcrumbs())

if __name__ == '__main__':
    framework()
