
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import re
import unittest
import zope

from Testing.ZopeTestCase import ZopeTestCase, FunctionalTestCase

from zope.interface import Interface, implements

from Products.Five.tests.products.FiveTest.classes import Adaptable, Origin
from Products.Five.tests.products.FiveTest.interfaces import IAdapted, IDestination
from Products.Five.tests.products.FiveTest.browser import SimpleContentView
from Products.Five.fiveconfigure import classDefaultViewable
from OFS.Traversable import Traversable

from Products.Five.tests.products.FiveTest.simplecontent import manage_addSimpleContent
from Products.Five.tests.products.FiveTest.simplecontent import manage_addCallableSimpleContent
from Products.Five.tests.products.FiveTest.simplecontent import manage_addIndexSimpleContent
from Products.Five.tests.products.FiveTest.fancycontent import manage_addFancyContent


def normalize_html(s):
    s = re.sub(r"[ \t\n]+", "", s)
    return s


class FiveTest(ZopeTestCase):

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

    def test_attribute_view(self):
        view = self.folder.unrestrictedTraverse('testoid/eagle.txt')
        self.assert_(isinstance(view, SimpleContentView))
        self.assertEquals('The eagle has landed', view())

    def test_existing_docstrings_arent_modified(self):
        view = self.folder.unrestrictedTraverse('testoid/eagle.txt')
        self.assertEquals(view.eagle.__doc__, SimpleContentView.eagle.__doc__)

    def test_pages_view(self):
        view = self.folder.unrestrictedTraverse('testoid/eagle-page.txt')
        self.assert_(isinstance(view, SimpleContentView))
        self.assertEquals('The eagle has landed', view())

        view = self.folder.unrestrictedTraverse('testoid/mouse-page.txt')
        self.assert_(isinstance(view, SimpleContentView))
        self.assertEquals('The mouse has been eaten by the eagle', view())

    def test_template_view(self):
        view = self.folder.unrestrictedTraverse('testoid/falcon.html')
        self.assert_(isinstance(view, SimpleContentView))
        self.assertEquals(u'<p>The falcon has taken flight</p>\n', view())

    def test_template_view_without_class(self):
        view = self.folder.unrestrictedTraverse('testoid/owl.html')
        self.assertEquals(u'<p>2</p>\n', view())

    def test_template_view_context(self):
        view = self.folder.unrestrictedTraverse('testoid/flamingo.html')
        self.assertEquals(u'<p>Hello world</p>\n', view())

    def test_template_view_context_path(self):
        view = self.folder.unrestrictedTraverse('testoid/flamingo2.html')
        self.assertEquals(u'<p>Hello world</p>\n', view())

    def test_template_view_resource_traversal(self):
        view = self.folder.unrestrictedTraverse('testoid/parakeet.html')
        expected = """\
        <html>
        <head>
        <title>bird macro</title>
        </head>
        <body>
        Color: green
        <img alt="" src="http://nohost/test_folder_1_/testoid/++resource++pattern.png" />
        </body>
        </html>
        """
        expected = normalize_html(expected)
        self.assertEquals(expected, normalize_html(view()))

    def test_view_backwards_compatibility(self):
        old_view = self.folder.unrestrictedTraverse('testoid/direct')
        self.assertEquals('Direct traversal worked', old_view())

    def test_zpt_things(self):
        view = self.folder.unrestrictedTraverse('testoid/condor.html')
        expected = """\
<p>Hello world</p>
<p>The eagle has landed</p>
<p>Hello world</p>
"""
        self.assertEquals(expected, view())

    def test_repeat(self):
        view = self.folder.unrestrictedTraverse('testoid/ostrich.html')
        expected = """\
<ul>
<li>Alpha</li>
<li>Beta</li>
<li>Gamma</li>
</ul>
"""
        self.assertEquals(expected, view())

    def test_repeat_iterator(self):
        view = self.folder.unrestrictedTraverse('testoid/ostrich2.html')
        expected = """\
<ul>
<li>0</li>
<li>1</li>
<li>2</li>
</ul>
"""
        self.assertEquals(expected, view())

    def test_tales_traversal(self):
        view = self.folder.unrestrictedTraverse('testoid/tales_traversal.html')
        expected = """\
<p>testoid</p>
<p>test_folder_1_</p>
"""
        self.assertEquals(expected, view())

    def test_zpt_security(self):
        self.logout()
        view = self.folder.unrestrictedTraverse('testoid/security.html')
        expected = """\
<div>NoneType</div>
<div>smtpd</div>
"""
        self.assertEquals(expected, view())

    def test_unrestrictedTraverse_non_existing(self):
        self.assertRaises(AttributeError, self.folder.unrestrictedTraverse,
                          'testoid/@@invalid_page')

    # Disabled __call__ overriding for now. Causes more trouble
    # than it fixes.
    # def test_existing_call(self):
    #     view = self.folder.unrestrictedTraverse('testcall')
    #     self.assertEquals("Default __call__ called", view())


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

class IRecurse(Interface):
    pass

class Recurse(Traversable):

    implements(IRecurse)

    def view(self):
        return self()

    def __call__(self):
        return 'foo'

classDefaultViewable(Recurse)

class RecursionTest(unittest.TestCase):

    def setUp(self):
        self.ob = Recurse()

    def test_recursive_call(self):
        from zope.app import zapi
        from zope.publisher.interfaces.browser import IBrowserRequest
        pres = zapi.getGlobalService('Presentation')
        type = IBrowserRequest
        pres.setDefaultViewName(IRecurse, type, 'view')
        self.assertEquals(self.ob.view(), 'foo')
        self.assertEquals(self.ob(), 'foo')

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
    suite.addTest(makeSuite(RecursionTest))
    suite.addTest(makeSuite(FiveTest))
    suite.addTest(makeSuite(PublishTest))
    suite.addTest(makeSuite(SizeTest))
    return suite

if __name__ == '__main__':
    framework()
