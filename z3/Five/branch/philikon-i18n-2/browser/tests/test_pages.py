##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
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
from Products.Five.tests.simplecontent import manage_addSimpleContent
from Products.Five.browser.tests.pages import SimpleView

def normalize_html(s):
    s = re.sub(r"[ \t\n]+", "", s)
    return s

class PagesTest(ZopeTestCase):

    def afterSetUp(self):
        zcml.load_config('pages.zcml', package=Products.Five.browser.tests)
        manage_addSimpleContent(self.folder, 'testoid', 'Testoid')
        uf = self.folder.acl_users
        uf._doAddUser('manager', 'r00t', ['Manager'], [])
        self.login('manager')

    def test_new_style_classes_are_ignored(self):
	# simple test: we import zope.app.form.browser which is full
	# of new-style classes
	zcml.load_string("""<include package="zope.app.form.browser"/>""")

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
        zcml.load_config('resource.zcml', package=Products.Five.browser.tests)
        view = self.folder.unrestrictedTraverse('testoid/parakeet.html')
        expected = """\
        <html>
        <body>
        <img alt="" src="http://nohost/test_folder_1_/testoid/++resource++pattern.png" />
        </body>
        </html>
        """
        expected = normalize_html(expected)
        self.assertEquals(expected, normalize_html(view()))

    def test_template_macro_access(self):
        view = self.folder.unrestrictedTraverse('testoid/seagull.html')
        self.assertEquals('<html><head><title>bird macro</title></head><body>Color: gray</body></html>\n', view())

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

    def test_overrides(self):
        zcml.load_string(
            """<includeOverrides
                   package="Products.Five.browser.tests"
                   file="overrides.zcml" />""")
        view = self.folder.unrestrictedTraverse('testoid/overridden_view')
        self.assertEquals(view(), "The mouse has been eaten by the eagle")

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PagesTest))
    return suite

if __name__ == '__main__':
    framework()
