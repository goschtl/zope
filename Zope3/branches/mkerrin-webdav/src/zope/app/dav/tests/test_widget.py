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
"""XXX - the tests in this file should be made a lot clearer.

$Id$
"""
__docformat__ = 'restructuredtext'

import datetime
from xml.dom import minidom
from unittest import TestSuite, main, makeSuite, TestCase

from zope.interface import Interface, implements
from zope.interface.verify import verifyClass
from zope.schema import Text, Datetime, Date, List, Tuple
from zope.schema import ValidationError
from zope.publisher.browser import TestRequest
from zope.testing.doctest import DocTestSuite

from zope.app.form.interfaces import WidgetInputError
from zope.app.testing import placelesssetup

from zope.app.dav.interfaces import IDAVWidget
from zope.app.dav.widget import DAVWidget, TextDAVWidget, DatetimeDAVWidget, \
     DateDAVWidget, XMLEmptyElementListDAVWidget, TupleDAVWidget


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

        self.failIf(self._widget.hasInput())
        self._widget.setRenderedValue(content)
        self.assert_(self._widget.hasInput())
        self.assert_(self._widget.hasValidInput())
        self.assertEqual(self._widget.getInputValue(), content)

    def _test_widget_bad_input(self, propel):
        self._widget.setProperty(propel)
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

class DatetimeDAVWidgetTest(DAVWidgetTest):
    _WidgetFactory = DatetimeDAVWidget
    _FieldFactory = Datetime

    test_content = datetime.datetime.fromtimestamp(1131234842)

    def test_widget_input(self):
        date = datetime.datetime(1999, 12, 31, 23, 59, 59)
        # date.strftime = '1999-12-31 23:59:59Z'

        doc = minidom.Document()
        propel = doc.createElement('foo')
        propel.appendChild(doc.createTextNode(date.strftime('%F')))
        self._widget.setProperty(propel)
        value = self._widget.getInputValue()
        fmt = '%y%m%d-000000'
        self.assertEqual(date.strftime(fmt), value.strftime(fmt))

        doc = minidom.Document()
        propel = doc.createElement('foo')
        propel.appendChild(
            doc.createTextNode(date.strftime('%a,  %d  %b %Y %H:%M:%S')))
        self._widget.setProperty(propel)
        value = self._widget.getInputValue()
        fmt = '%y%m%d-%H%M%S'
        self.assertEqual(date.strftime(fmt), value.strftime(fmt))

    def test_widget_bad_input(self):
        doc = minidom.Document()
        propel = doc.createElement('foo')
        propel.appendChild(doc.createTextNode('invalid datetime content'))
        super(DatetimeDAVWidgetTest, self)._test_widget_bad_input(propel)


class DateDAVWidgetTest(DAVWidgetTest):
    _WidgetFactory = DateDAVWidget
    _FieldFactory  = Date

    test_content = datetime.date.fromtimestamp(1131234842)

    def test_widget_input(self):
        dateinst = datetime.datetime(1999, 12, 31, 23, 59, 59).date()
        doc = minidom.Document()
        propel = doc.createElement('foo')
        # date.strftime = '1999-12-31 23:59:59Z'
        propel.appendChild(doc.createTextNode(dateinst.strftime('%F')))
        self._widget.setProperty(propel)

        value = self._widget.getInputValue()
        self.assertEqual(value, dateinst)

    def test_widget_bad_input(self):
        doc = minidom.Document()
        propel = doc.createElement('foo')
        propel.appendChild(doc.createTextNode('invalid date content'))
        super(DateDAVWidgetTest, self)._test_widget_bad_input(propel)


class XMLEmptyElementListDAVWidgetTest(DAVWidgetTest):
    _WidgetFactory = XMLEmptyElementListDAVWidget
    _FieldFactory = List

    test_content = [u'hello', u'there']
    test_bad_contents = [10, u'hello']


class TupleDAVWidgetTest(DAVWidgetTest):
    _WidgetFactory = TupleDAVWidget
    _FieldFactory = Tuple

    test_content = (u'hello', u'there')
    test_bad_contents = [10, u'hello']


def test_suite():
    return TestSuite((
        makeSuite(TextDAVWidgetTest),
        makeSuite(DatetimeDAVWidgetTest),
        makeSuite(DateDAVWidgetTest),
        makeSuite(XMLEmptyElementListDAVWidgetTest),
        makeSuite(TupleDAVWidgetTest),
        DocTestSuite('zope.app.dav.widget'),
        ))

if __name__ == '__main__':
    main(defaultTest = 'test_suite')
