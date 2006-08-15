##############################################################################
#
# Copyright (c) 2005 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Tests of the widget code for comment text.

"""
__docformat__ = "reStructuredText"

import unittest

from zope.app.form.browser.tests import test_browserwidget

import zc.comment.interfaces
import zc.comment.browser.widget


class TestBase(object):

    _FieldFactory = zc.comment.interfaces.CommentText


class DisplayWidgetTestCase(TestBase, test_browserwidget.BrowserWidgetTest):
    """Tests of the display widget."""

    _WidgetFactory = zc.comment.browser.widget.Display

    def test_render_empty_string(self):
        self._widget.setRenderedValue("")
        self.assertEqual(self._widget(),
                         '<div class="zc-comment-text"></div>')

    def test_render_multiline(self):
        self._widget.setRenderedValue("line 1<br />\n<br />\nline 2")
        self.assertEqual(self._widget(),
                         '<div class="zc-comment-text">line 1<br />\n'
                         '<br />\n'
                         'line 2</div>')

    def test_render_missing_value(self):
        self._widget.setRenderedValue(self._widget.context.missing_value)
        self.assertEqual(self._widget(), '')


class InputWidgetTestCase(TestBase, test_browserwidget.BrowserWidgetTest):

    _WidgetFactory = zc.comment.browser.widget.Input

    def setUp(self):
        super(InputWidgetTestCase, self).setUp()
        self.clearForm()

    def clearForm(self):
        form = self._widget.request.form
        if "field.foo" in form:
            del form["field.foo"]

    def test_hasInput(self):
        self.failIf(self._widget.hasInput())
        form = self._widget.request.form
        form["field.foo"] = u'some text'
        self.failUnless(self._widget.hasInput())
        self._widget.setRenderedValue(u"other text")
        self.failUnless(self._widget.hasInput())
        self.clearForm()
        self.failIf(self._widget.hasInput())

    def test_getInputValue_one_line(self):
        self._widget.request.form["field.foo"] = u'line of text'
        self.assertEqual(self._widget.getInputValue(), u'line of text')

    def test_getInputValue_multi_line(self):
        self._widget.request.form["field.foo"] = u'line 1\rline 2'
        self.assertEqual(self._widget.getInputValue(), u'line 1<br />\nline 2')

    def test_render_missing_value(self):
        self._widget.setRenderedValue(self._widget.context.missing_value)
        self.verifyResult(self._widget(),
                          ['<textarea', 'class="zc-comment-text"',
                           '></textarea>'],
                          inorder=True)

    def test_render_empty_string(self):
        self._widget.setRenderedValue("")
        self.verifyResult(self._widget(),
                          ['<textarea', 'class="zc-comment-text"',
                           '></textarea>'],
                          inorder=True)

    def test_render_multi_line(self):
        self._widget.setRenderedValue(u"line 1<br />\n<br />\nline 3"
                                      u" &lt; &amp; &gt; ")
        self.verifyResult(self._widget(),
                          ['<textarea', 'class="zc-comment-text"',
                           'line 1\n\nline 3', '&lt; &amp; &gt; </textarea'],
                          inorder=True)


def test_suite():
    suite = unittest.TestSuite()
    for cls in (DisplayWidgetTestCase,
                InputWidgetTestCase,
                ):
        suite.addTest(unittest.makeSuite(cls))
    return suite
