##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Sequence Field Widget tests.

$Id$
"""
import unittest, doctest

from zope.schema import Tuple, List, TextLine
from zope.schema.interfaces import ITextLine, ValidationError
from zope.publisher.browser import TestRequest
from zope.interface import Interface, implements
from zope.interface.verify import verifyClass

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.form.browser import TextWidget, TupleSequenceWidget
from zope.app.form.browser import ListSequenceWidget
from zope.app.form.interfaces import IInputWidget

from zope.app.form.browser.tests.test_browserwidget import BrowserWidgetTest


class SequenceWidgetTest(BrowserWidgetTest):
    """Documents and tests the tuple and list (sequence) widgets.
    
        >>> verifyClass(IInputWidget, TupleSequenceWidget)
        True
        >>> verifyClass(IInputWidget, ListSequenceWidget)
        True
    """

    def setUpContent(self, desc=u'', title=u'Foo Title'):
        class ITestContent(Interface):
            foo = self._FieldFactory(
                    title=title,
                    description=desc,
                    )
        class TestObject(object):
            implements(ITestContent)

        self.content = TestObject()
        field = ITestContent['foo']
        field = field.bind(self.content)
        request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl')
        request.form['field.foo'] = u'Foo Value'
        # sequence widgets take value_type as second argument because of double
        # dispatch
        self._widget = self._WidgetFactory(field, TextLine(), request)

    def _FieldFactory(self, **kw):
        kw.update({
            '__name__': u'foo', 
            'value_type': TextLine(__name__=u'bar')})
        return Tuple(**kw)
    _WidgetFactory = TupleSequenceWidget

    def testRender(self):
        pass

    def setUp(self):
        BrowserWidgetTest.setUp(self)
        self.field = Tuple(
            __name__=u'foo',
            value_type=TextLine(__name__=u'bar'))
        ztapi.browserViewProviding(ITextLine, TextWidget, IInputWidget)

    def test_haveNoData(self):
        self.failIf(self._widget.hasInput())

    def test_hasInput(self):
        self._widget.request.form['field.foo.0.bar'] = u'hi, mum'
        self.failUnless(self._widget.hasInput())

    def test_list(self):
        self.field = List(
            __name__=u'foo',
            value_type=TextLine(__name__=u'bar'))
        request = TestRequest()
        widget = ListSequenceWidget(self.field, TextLine(), request)
        self.failIf(widget.hasInput())
        self.assertEquals(widget.getInputValue(), [])

        request = TestRequest(form={'field.foo.add': u'Add bar'})
        widget = ListSequenceWidget(self.field, TextLine(), request)
        self.assert_(widget.hasInput())
        self.assertRaises(ValidationError, widget.getInputValue)

        request = TestRequest(form={'field.foo.0.bar': u'Hello world!'})
        widget = ListSequenceWidget(self.field, TextLine(), request)
        self.assert_(widget.hasInput())
        self.assertEquals(widget.getInputValue(), [u'Hello world!'])

    def test_new(self):
        request = TestRequest()
        widget = TupleSequenceWidget(self.field, TextLine(), request)
        self.failIf(widget.hasInput())
        self.assertEquals(widget.getInputValue(), ())
        check_list = ('input', 'name="field.foo.add"')
        self.verifyResult(widget(), check_list)

    def test_add(self):
        request = TestRequest(form={'field.foo.add': u'Add bar'})
        widget = TupleSequenceWidget(self.field, TextLine(), request)
        self.assert_(widget.hasInput())
        self.assertRaises(ValidationError, widget.getInputValue)
        check_list = (
            'checkbox', 'field.foo.remove_0', 'input', 'field.foo.0.bar',
            'submit', 'submit', 'field.foo.add'
        )
        self.verifyResult(widget(), check_list, inorder=True)

    def test_request(self):
        request = TestRequest(form={'field.foo.0.bar': u'Hello world!'})
        widget = TupleSequenceWidget(self.field, TextLine(), request)
        self.assert_(widget.hasInput())
        self.assertEquals(widget.getInputValue(), (u'Hello world!',))

    def test_existing(self):
        request = TestRequest()
        widget = TupleSequenceWidget(self.field, TextLine(), request)
        widget.setRenderedValue((u'existing',))
        self.assert_(widget.hasInput())
        self.assertEquals(widget.getInputValue(), (u'existing',))
        check_list = (
            'checkbox', 'field.foo.remove_0', 'input', 'field.foo.0.bar',
                'existing',
            'submit', 'submit', 'field.foo.add'
        )
        self.verifyResult(widget(), check_list, inorder=True)
        widget.setRenderedValue((u'existing', u'second'))
        self.assert_(widget.hasInput())
        self.assertEquals(widget.getInputValue(), (u'existing', u'second'))
        check_list = (
            'checkbox', 'field.foo.remove_0', 'input', 'field.foo.0.bar',
                'existing',
            'checkbox', 'field.foo.remove_1', 'input', 'field.foo.1.bar',
                'second',
            'submit', 'submit', 'field.foo.add'
        )
        self.verifyResult(widget(), check_list, inorder=True)

    def test_remove(self):
        request = TestRequest(form={'field.foo.remove_0': u'Hello world!',
            'field.foo.0.bar': u'existing', 'field.foo.1.bar': u'second',
            'remove-selected-items-of-seq-field.foo': u'Remove selected items'})
        widget = TupleSequenceWidget(self.field, TextLine(), request)
        widget.setRenderedValue((u'existing', u'second'))
        self.assertEquals(widget.getInputValue(), (u'second',))
        check_list = (
            'checkbox', 'field.foo.remove_0', 'input', 'field.foo.0.bar',
                'second',
            'submit', 'submit', 'field.foo.add'
        )
        self.verifyResult(widget(), check_list, inorder=True)

    def test_min(self):
        request = TestRequest()
        self.field.min_length = 2
        widget = TupleSequenceWidget(self.field, TextLine(), request)
        widget.setRenderedValue((u'existing',))
        self.assertEquals(widget.getInputValue(), (u'existing',))
        check_list = (
            'input', 'field.foo.0.bar', 'existing',
            'input', 'field.foo.1.bar', 'value=""',
            'submit', 'field.foo.add'
        )
        s = widget()
        self.verifyResult(s, check_list, inorder=True)
        self.assertEquals(s.find('checkbox'), -1)

    def test_max(self):
        request = TestRequest()
        self.field.max_length = 1
        widget = TupleSequenceWidget(self.field, TextLine(), request)
        widget.setRenderedValue((u'existing',))
        self.assertEquals(widget.getInputValue(), (u'existing',))
        s = widget()
        self.assertEquals(s.find('field.foo.add'), -1)

    def test_anonymousfield(self):
        self.field = Tuple(__name__=u'foo', value_type=TextLine())
        request = TestRequest()
        widget = TupleSequenceWidget(self.field, TextLine(), request)
        widget.setRenderedValue((u'existing',))
        s = widget()
        check_list = (
            'input', '"field.foo.0."', 'existing',
            'submit', 'submit', 'field.foo.add'
        )
        s = widget()
        self.verifyResult(s, check_list, inorder=True)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(SequenceWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')


