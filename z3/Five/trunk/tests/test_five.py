import os, sys
from os import curdir
from os.path import join, abspath, dirname, split

try:
    __file__
except NameError:
    # Test was called directly, so no __file__ global exists.
    _prefix = abspath(curdir)
else:
    # Test was called by another test.
    _prefix = abspath(dirname(__file__))

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# XXX hack but no other way to initialize options apparently
from Zope.Startup.run import configure
configure(join(_prefix, '..', '..', '..', 'etc', 'zope.conf'))

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
        test = self.root.testoid
        view = self.root.unrestrictedTraverse('testoid/eagle.txt')
        self.assert_(isinstance(view, SimpleContentView))
        self.assertEquals('The eagle has landed', view())

    def test_template_view(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.root.unrestrictedTraverse('testoid/falcon.html')
        self.assert_(isinstance(view, SimpleContentView))
        self.assertEquals(u'<p>The falcon has taken flight</p>\n', view())

    def test_template_view_without_class(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.root.unrestrictedTraverse('testoid/owl.html')
        self.assertEquals(u'<p>2</p>\n', view())

    def test_template_view_context(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.root.unrestrictedTraverse('testoid/flamingo.html')
        self.assertEquals(u'<p>Hello world</p>\n', view())

    def test_template_view_context_path(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.root.unrestrictedTraverse('testoid/flamingo2.html')
        self.assertEquals(u'<p>Hello world</p>\n', view())

    def test_view_backwards_compatibility(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        old_view = self.root.unrestrictedTraverse('testoid/direct')
        self.assertEquals('Direct traversal worked', old_view())

    def test_zpt_things(self):
        self.root.manage_addProduct['FiveTest'].manage_addSimpleContent(
            'testoid', 'Testoid')
        view = self.root.unrestrictedTraverse('testoid/condor.html')
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

