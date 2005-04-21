##############################################################################
#
# Copyright (c) 2005 Five Contributors. All rights reserved.
#
# This software is distributed under the terms of the Zope Public
# License (ZPL) v2.1. See COPYING.txt for more information.
#
##############################################################################
"""Test browser pages

$Id$
"""
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import unittest
from Testing.ZopeTestCase import ZopeTestCase, installProduct
installProduct('Five')

import re
import Products.Five.browser.tests
from Products.Five import zcml
from Products.Five.browser.tests.pages import SimpleView
from Products.Five.browser.tests.simplecontent import manage_addSimpleContent

def normalize_html(s):
    s = re.sub(r"[ \t\n]+", "", s)
    return s

class PagesTest(ZopeTestCase):

    def afterSetUp(self):
	zcml.load_config('pages.zcml', package=Products.Five.browser.tests)
	manage_addSimpleContent(self.folder, 'testoid', 'Testoid')

    def test_attribute_view(self):
        view = self.folder.unrestrictedTraverse('testoid/eagle.txt')
        self.assert_(isinstance(view, SimpleView))
        self.assertEquals('The eagle has landed', view())

    def test_existing_docstrings_arent_modified(self):
        view = self.folder.unrestrictedTraverse('testoid/eagle.txt')
        self.assertEquals(view.eagle.__doc__, SimpleView.eagle.__doc__)

    def test_pages_view(self):
        view = self.folder.unrestrictedTraverse('testoid/eagle-page.txt')
        self.assert_(isinstance(view, SimpleView))
        self.assertEquals('The eagle has landed', view())

        view = self.folder.unrestrictedTraverse('testoid/mouse-page.txt')
        self.assert_(isinstance(view, SimpleView))
        self.assertEquals('The mouse has been eaten by the eagle', view())

    def test_template_view(self):
        view = self.folder.unrestrictedTraverse('testoid/falcon.html')
        self.assert_(isinstance(view, SimpleView))
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

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PagesTest))
    return suite

if __name__ == '__main__':
    framework()
