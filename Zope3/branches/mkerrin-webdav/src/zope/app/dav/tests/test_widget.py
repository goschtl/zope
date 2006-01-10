##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""
$Id$
"""
__docformat__ = 'restructuredtext'

from datetime import datetime
from xml.dom import minidom
from unittest import TestSuite, main, makeSuite, TestCase

from zope.interface import Interface, implements
from zope.interface.verify import verifyClass
from zope.schema import Text, Datetime, List
from zope.schema import ValidationError
from zope.publisher.browser import TestRequest
from zope.testing.doctest import DocTestSuite

from zope.app.form.interfaces import WidgetInputError
from zope.app.testing import placelesssetup

from zope.app.dav.interfaces import IDAVWidget
from zope.app.dav.widget import DAVWidget, TextDAVWidget, DatetimeDAVWidget, \
     XMLEmptyElementListDAVWidget


class DAVWidgetTest(placelesssetup.PlacelessSetup, TestCase):

    _FieldFactory = Text
    _WidgetFactory = DAVWidget

    def setUp(self):
        desc = u''
        title = u'Foo Title'
        foofield = self._FieldFactory(title = title, description = desc)
        class ITestContent(Interface):
            foo = foofield

        class TestObject(object):
            implements(ITestContent)

        self.content = TestObject()
        field = ITestContent['foo']
        field = field.bind(self.content)
        request = TestRequest(HTTP_ACCEPT_LANGUAGE = 'pl')
        request.form['field.foo'] = u'Foo Value'
        self._widget = self._WidgetFactory(field, request)

    def test_base_interface(self):
        self.failUnless(verifyClass(IDAVWidget, DAVWidget))

    def test_widget_input(self):
        content = self.test_content
        # try multiple bad content
        bad_contents = self.test_bad_contents
        if not isinstance(bad_contents, list):
            bad_contents = [bad_contents]

        self.failIf(self._widget.hasInput())
        self._widget.setRenderedValue(content)
        self.assert_(self._widget.hasInput())
        self.assert_(self._widget.hasValidInput())
        self.assertEqual(self._widget.getInputValue(), content)

        for bad_content in bad_contents:
            self._widget.setRenderedValue(bad_content)
            self.assert_(self._widget.hasInput())
            self.failIf(self._widget.hasValidInput())
            self.assertRaises(WidgetInputError, self._widget.getInputValue)

    def test_widget_apply_content(self):
        content = self.test_content

        self._widget.setRenderedValue(content)
        self.assert_(self._widget.hasValidInput())

        self.assert_(self._widget.applyChanges(self.content))


class TextDAVWidgetTest(DAVWidgetTest):
    _WidgetFactory = TextDAVWidget

    test_content = u'This is some text content'
    test_bad_contents = 10


class DatetimeDAVWidgetTest(DAVWidgetTest):
    _WidgetFactory = DatetimeDAVWidget
    _FieldFactory = Datetime

    test_content = datetime.fromtimestamp(1131234842)
    test_bad_contents = [10, u'This is bad content']

    def test_widget_input(self):
        date = datetime(1999, 12, 31, 23, 59, 59)
        doc = minidom.Document()
        propel = doc.createElement('foo')
        # date.strftime = '1999-12-31 23:59:59Z'
        propel.appendChild(doc.createTextNode(date.strftime('%F')))
        self._widget.setProperty(propel)
        ## self._widget._value == date
        ## TypeError: can't compare offset-naive and offset-aware datetimes


class XMLEmptyElementListDAVWidgetTest(DAVWidgetTest):
    _WidgetFactory = XMLEmptyElementListDAVWidget
    _FieldFactory = List

    test_content = [u'hello', u'there']
    test_bad_contents = [10, u'hello']


def test_suite():
    return TestSuite((
        makeSuite(TextDAVWidgetTest),
        makeSuite(DatetimeDAVWidgetTest),
        makeSuite(XMLEmptyElementListDAVWidgetTest),
        DocTestSuite('zope.app.dav.widget'),
        ))

if __name__ == '__main__':
    main(defaultTest = 'test_suite')
