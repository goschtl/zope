import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing import ZopeTestCase

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('FiveTest')

from zope.component import getAdapter
from Products.FiveTest.classes import Adaptable
from Products.FiveTest.interfaces import IAdapted
from Products.FiveTest.browser import SimpleContentView

class FiveTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        uf = self.folder.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        self.login('manager')

    def test_adapters(self):
        obj = Adaptable()
        adapted = getAdapter(obj, IAdapted)
        self.assertEquals(
            "Adapted: The method",
            adapted.adaptedMethod())

    def test_adapters2(self):
        obj = Adaptable()
        adapted = IAdapted(obj)
        self.assertEquals(
            "Adapted: The method",
            adapted.adaptedMethod())

    def test_attribute_view(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        test = self.folder.testoid
        view = self.folder.unrestrictedTraverse('testoid/eagle.txt')
        self.assert_(isinstance(view, SimpleContentView))
        self.assertEquals('The eagle has landed', view())

    def test_template_view(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.folder.unrestrictedTraverse('testoid/falcon.html')
        self.assert_(isinstance(view, SimpleContentView))
        self.assertEquals(u'<p>The falcon has taken flight</p>\n', view())

    def test_template_view_without_class(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.folder.unrestrictedTraverse('testoid/owl.html')
        self.assertEquals(u'<p>2</p>\n', view())

    def test_template_view_context(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.folder.unrestrictedTraverse('testoid/flamingo.html')
        self.assertEquals(u'<p>Hello world</p>\n', view())

    def test_template_view_context_path(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.folder.unrestrictedTraverse('testoid/flamingo2.html')
        self.assertEquals(u'<p>Hello world</p>\n', view())

    def test_view_backwards_compatibility(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        old_view = self.folder.unrestrictedTraverse('testoid/direct')
        self.assertEquals('Direct traversal worked', old_view())

    def test_zpt_things(self):
        self.folder.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.folder.unrestrictedTraverse('testoid/condor.html')
        expected = """\
<p>Hello world</p>
<p>The eagle has landed</p>
<p>Hello world</p>
"""
        self.assertEquals(expected, view())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FiveTestCase))
    return suite

if __name__ == '__main__':
    framework()
