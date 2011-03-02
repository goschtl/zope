##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
import os
import persistent
import pytz
import re
import unittest
import zope.component
import zope.interface
import zope.interface.common.idatetime
import zope.app.form.interfaces
import zope.app.testing.functional
import zope.publisher.browser
import zope.testing.renormalizing
import zc.table
from zope.app.form.browser.tests import test_browserwidget
from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer

import zc.comment.interfaces
import zc.comment.browser.widget


CommentsLayer = ZCMLLayer(
    os.path.join(
        os.path.split(zc.comment.browser.__file__)[0], 'ftesting.zcml'),
    __name__, 'CommentsLayer', allow_teardown=True)


class IFace(zope.interface.Interface):
    foo = zc.comment.interfaces.CommentText(
        title=u"Foo",
        description=u"Foo description",
        )

class Face(object):
    foo = (u"Foo<br />\n"
           u"\n"
           u"Bar &lt; &amp; &gt;")


class MyContent(persistent.Persistent):
    x = 0

@zope.component.adapter(zope.publisher.interfaces.IRequest)
@zope.interface.implementer(zope.interface.common.idatetime.ITZInfo)
def requestToTZInfo(request):
    return pytz.timezone('US/Eastern')

def formatterFactory(*args, **kw):
    return zc.table.table.FormFullFormatter(*args, **kw)
zope.interface.directlyProvides(formatterFactory,
                                zc.table.interfaces.IFormatterFactory)


class WidgetConfigurationTestCase(unittest.TestCase):
    """Check that configure.zcml sets up the widgets as expected."""

    def setUp(self):
        super(WidgetConfigurationTestCase, self).setUp()
        self.field = IFace["foo"]
        self.bound_field = self.field.bind(Face())
        self.request = zope.publisher.browser.TestRequest()

    def test_display_widget_lookup(self):
        w = zope.component.getMultiAdapter(
            (self.bound_field, self.request),
             zope.app.form.interfaces.IDisplayWidget)
        self.failUnless(isinstance(w, zc.comment.browser.widget.Display))

    def test_input_widget_lookup(self):
        w = zope.component.getMultiAdapter(
            (self.bound_field, self.request),
             zope.app.form.interfaces.IInputWidget)
        self.failUnless(isinstance(w, zc.comment.browser.widget.Input))


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
    suites = []
    for cls in (DisplayWidgetTestCase,
                InputWidgetTestCase,
                ):
        suites.append(unittest.makeSuite(cls))

    widgetConfig = unittest.makeSuite(WidgetConfigurationTestCase)
    widgetConfig.layer = CommentsLayer
    suites.append(widgetConfig)

    checker = zope.testing.renormalizing.RENormalizing([
        (re.compile(r'\d\d\d\d \d\d? \d\d?\s+\d\d:\d\d:\d\d( [+-]\d+)?'),
         'YYYY MM DD  HH:MM:SS'),
        ])

    readme = FunctionalDocFileSuite(
        os.path.join('README.txt'), checker=checker)
    readme.layer = CommentsLayer
    suites.append(readme)

    return unittest.TestSuite(suites)
