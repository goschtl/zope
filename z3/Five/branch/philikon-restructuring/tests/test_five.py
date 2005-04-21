
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import re
import unittest
import zope

from Testing.ZopeTestCase import ZopeTestCase, FunctionalTestCase

from Products.Five.tests.products.FiveTest.classes import Adaptable, Origin
from Products.Five.tests.products.FiveTest.interfaces import IAdapted, IDestination
from Products.Five.tests.products.FiveTest.browser import SimpleContentView

from Products.Five.tests.products.FiveTest.simplecontent import manage_addSimpleContent
from Products.Five.tests.products.FiveTest.simplecontent import manage_addCallableSimpleContent
from Products.Five.tests.products.FiveTest.simplecontent import manage_addIndexSimpleContent
from Products.Five.tests.products.FiveTest.fancycontent import manage_addFancyContent


class FiveTest(ZopeTestCase):
    """Test very basic Five functionality (adapters, ZCML, etc.)"""

    def afterSetUp(self):
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        manage_addCallableSimpleContent(self.folder, 'testcall', 'TestCall')
        manage_addIndexSimpleContent(self.folder, 'testindex', 'TestIndex')
        uf = self.folder.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        self.login('manager')

    def test_adapters(self):
        obj = Adaptable()
        adapted = IAdapted(obj)
        self.assertEquals(
            "Adapted: The method",
            adapted.adaptedMethod())

    def test_adapters2(self):
        obj = Adaptable()
        adapted = IAdapted(obj)
        self.assertEquals(
            "Adapted: The method",
            adapted.adaptedMethod())

    def test_overrides(self):
        origin = Origin()
        dest = IDestination(origin)
        self.assertEquals(dest.method(), "Overridden")

        view = self.folder.unrestrictedTraverse('testoid/overridden_view')
        self.assertEquals(view(), "The mouse has been eaten by the eagle")

class PublishTest(FunctionalTestCase):
    """Test a few publishing features"""

    def afterSetUp(self):
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        manage_addCallableSimpleContent(self.folder, 'testcall', 'TestCall')
        manage_addIndexSimpleContent(self.folder, 'testindex', 'TestIndex')
        uf = self.folder.acl_users
        uf._doAddUser('viewer', 'secret', [], [])
        uf._doAddUser('manager', 'r00t', ['Manager'], [])

    def test_no_doc_string(self):
        for view_name in ['nodoc-function', 'nodoc-method', 'nodoc-object']:
            response = self.publish('/test_folder_1_/testoid/%s' % view_name)
            self.assertEquals("No docstring", response.getBody())

    def test_fallback_raises_notfound(self):
        # If we return None in __fallback_traverse__, this test passes
        # but for the wrong reason: None doesn't have a docstring so
        # BaseRequest raises NotFoundError. A functional test would be
        # perfect here.
        response = self.publish('/test_folder_1_/testoid/doesntexist')
        self.assertEquals(404, response.getStatus())

    def test_existing_bobo_traverse(self):
        manage_addFancyContent(self.folder, 'fancy', '')

        # check if the old bobo_traverse method can still kick in
        response = self.publish('/test_folder_1_/fancy/something-else')
        self.assertEquals('something-else', response.getBody())

        # check if z3-based view lookup works
        response = self.publish('/test_folder_1_/fancy/fancy')
        self.assertEquals("Fancy, fancy", response.getBody())

    # Disabled __call__ overriding for now. Causes more trouble
    # than it fixes.
    # def test_existing_call(self):
    #     response = self.publish('/test_folder_1_/testcall')
    #     self.assertEquals("Default __call__ called", response.getBody())

    def test_existing_index(self):
        response = self.publish('/test_folder_1_/testindex')
        self.assertEquals("Default index_html called", response.getBody())

    def test_default_view(self):
        response = self.publish('/test_folder_1_/testoid', basic='manager:r00t')
        self.assertEquals("The eagle has landed", response.getBody())

    def test_pages_from_directory(self):
        response = self.publish('/test_folder_1_/testoid/dirpage1')
        self.assert_('page 1' in response.getBody())
        response = self.publish('/test_folder_1_/testoid/dirpage2')
        self.assert_('page 2' in response.getBody())

class SizeTest(ZopeTestCase):

    def test_no_get_size_on_original(self):
        manage_addSimpleContent(self.folder, 'simple', 'Simple')
	obj = self.folder.simple
	self.assertEquals(obj.get_size(), 42)

    def test_get_size_on_original_and_fallback(self):
	manage_addFancyContent(self.folder, 'fancy', 'Fancy')
	obj = self.folder.fancy
	self.assertEquals(obj.get_size(), 43)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(FiveTest))
    suite.addTest(makeSuite(PublishTest))
    suite.addTest(makeSuite(SizeTest))
    return suite

if __name__ == '__main__':
    framework()
