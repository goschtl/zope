##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
import unittest

class TestRecorderTests(unittest.TestCase):

    def _getTargetClass(self):
        from zope.testrecorder.testrecorder import TestRecorder
        return TestRecorder

    def _makeOne(self, id='test', title=''):
        return self._getTargetClass()(id, title)

    def test_has_resource_html(self):
        from Products.PageTemplates.PageTemplateFile import PageTemplateFile
        recorder = self._makeOne()
        index = getattr(recorder, 'index.html', None)
        self.failUnless(isinstance(index, PageTemplateFile))

    def test_index_html_has_docstring(self):
        klass = self._getTargetClass()
        index_html = klass.index_html.im_func
        self.failUnless(index_html.__doc__)

    def test_index_html_redirects(self):
        from OFS.Folder import Folder
        root = Folder()
        recorder = self._makeOne().__of__(root)
        response = DummyResponse()
        request = {'RESPONSE': response}
        recorder.index_html(request)
        self.assertEqual(response._redirected,
                         'test/index.html')

class DummyResponse:

    _redirected = None

    def redirect(self, url):
        self._redirected = url


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestRecorderTests),
    ))
