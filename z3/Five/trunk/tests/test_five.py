import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# XXX hack but no other way to initialize options apparently
from Zope.Startup.run import configure
configure('../../../etc/zope.conf')

from Testing import ZopeTestCase

ZopeTestCase.installProduct('Five')
ZopeTestCase.installProduct('FiveTest')

from zope.component import getAdapter
from Products.FiveTest.classes import Adaptable
from Products.FiveTest.interfaces import IAdapted
from Products.FiveTest.browser import SimpleContentView

class FiveTestCase(ZopeTestCase.ZopeTestCase):
    def beforeSetUp(self):
        self.root = self._app()

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
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        test = self.root.test
        view = self.root.unrestrictedTraverse('testoid/eagle.txt')
        self.assert_(isinstance(view, SimpleContentView))
        data = view()
        self.assertEquals('The eagle has landed', data)

    def test_template_view(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.root.unrestrictedTraverse('testoid/falcon.html')
        self.assert_(isinstance(view, SimpleContentView))
        data = view()
        self.assertEquals(u'<p>The falcon has taken flight</p>\n', data)

    def test_template_view_without_class(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.root.unrestrictedTraverse('testoid/owl.html')
        data = view()
        self.assertEquals(u'<p>2</p>\n', data)

    def test_template_view_context(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.root.unrestrictedTraverse('testoid/flamingo.html')
        data = view()
        self.assertEquals(u'<p>Hello world</p>\n', data)
        
    def test_view_backwards_compatibility(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        old_view = self.root.unrestrictedTraverse('testoid/direct')
        data = old_view()
        self.assertEquals('Direct traversal worked', data)
        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(FiveTestCase))
        return suite
