##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test browser resources

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

import glob
import Products.Five.browser.tests
from Products.Five import zcml
from Products.Five.browser.resource import Resource, PageTemplateResource
from Products.Five.tests.helpers import manage_addFiveTraversableFolder

_prefix = os.path.dirname(Products.Five.browser.tests.__file__)
dir_resource_names = [os.path.basename(r)
                      for r in (glob.glob('%s/*.png' % _prefix) +
                                glob.glob('%s/*.pt' % _prefix) +
                                glob.glob('%s/[a-z]*.py' % _prefix) +
                                glob.glob('%s/*.css' % _prefix))]

class AbsoluteURLTests(ZopeTestCase):

    def afterSetUp(self):
	zcml.load_config('configure.zcml', package=Products.Five.browser.tests)
	manage_addFiveTraversableFolder(self.folder, 'testoid', 'Testoid')

    def test_template_resource(self):
        resource = self.folder.unrestrictedTraverse('testoid/++resource++cockatiel.html')
        self.assert_(isinstance(resource, Resource))
        expected = """\
<p>Have you ever seen a cockatiel?</p>
<p>maybe</p>
"""
        self.assertEquals(expected, resource())

    def test_file_resource(self):
        resource = self.folder.unrestrictedTraverse('testoid/++resource++style.css')
        self.assert_(isinstance(resource, Resource))
        expected = 'http://nohost/test_folder_1_/testoid/++resource++style.css'
        self.assertEquals(expected, resource())

    def test_image_resource(self):
        resource = self.folder.unrestrictedTraverse('testoid/++resource++pattern.png')
        expected = 'http://nohost/test_folder_1_/testoid/++resource++pattern.png'
        self.assert_(isinstance(resource, Resource))
        self.assertEquals(expected, resource())

    def test_resource_directory(self):
        base = 'testoid/++resource++fivetest_resources/%s'
        base_url = 'test_folder_1_/%s' % base
        for r in dir_resource_names:
            resource = self.folder.unrestrictedTraverse(base % r)
            self.assert_(isinstance(resource, Resource))
            # PageTemplateResource's __call__ renders the template
            if not isinstance(resource, PageTemplateResource):
                self.assertEquals(resource(), base_url % r)
        abs_url = self.folder.unrestrictedTraverse(base % '')()
        expected = 'http://nohost/test_folder_1_/testoid/++resource++fivetest_resources'
        self.assertEquals(abs_url, expected)

if __name__ == '__main__':
    framework()
