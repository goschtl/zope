##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: test_objectwidget.py,v 1.1 2003/07/13 06:47:18 richard Exp $
"""

import unittest

from zope.interface import Interface, implements
from zope.component.view import provideView
from zope.schema.interfaces import ITextLine, ValidationError
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.publisher.browser import TestRequest
from zope.schema import Object, TextLine
from zope.app.browser.form.widget import TextWidget, ObjectWidget
from zope.app.component.metaconfigure import resolveInterface

from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest

class ITestContact(Interface):
    name = TextLine()
    email = TextLine()
class TestContact:
    implements(ITestContact)

class ObjectWidgetTest(BrowserWidgetTest):
    _FieldFactory = Object
    def _WidgetFactory(self, context, request, **kw):
        kw.update({'factory': TestContact})
        return ObjectWidget(context, request, **kw)

    def setUpContent(self):
        provideView(ITextLine, 'edit', IBrowserPresentation, [TextWidget])

        class ITestContent(Interface):
            foo = self._FieldFactory(ITestContact, title = u"Foo Title")
        class TestObject:
            implements(ITestContent)

        self.content = TestObject()
        self.field = ITestContent['foo']
        self.request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl')
        self.request.form['field.foo'] = u'Foo Value'
        self._widget = self._WidgetFactory(self.field, self.request)

    def test_haveData(self):
        # doesn't work with subfields
        pass

    def testRender(self):
        # doesn't work with subfields
        pass

    def setUp(self):
        BrowserWidgetTest.setUp(self)
        self.field = Object(ITestContact, __name__=u'foo')
        provideView(ITextLine, 'edit', IBrowserPresentation, [TextWidget])

    def test_applyChanges(self):
        self.request.form['field.foo.name'] = u'Foo Name'
        self.request.form['field.foo.email'] = u'foo@foo.test'
        widget = self._WidgetFactory(self.field, self.request)

        self.assertEqual(widget.applyChanges(self.content), True)
        self.assertEqual(hasattr(self.content, 'foo'), True)
        self.assertEqual(isinstance(self.content.foo, TestContact), True)
        self.assertEqual(self.content.foo.name, u'Foo Name')
        self.assertEqual(self.content.foo.email, u'foo@foo.test')

    def test_applyChangesNoChange(self):
        self.content.foo = TestContact()
        self.content.foo.name = u'Foo Name'
        self.content.foo.email = u'foo@foo.test'

        self.request.form['field.foo.name'] = u'Foo Name'
        self.request.form['field.foo.email'] = u'foo@foo.test'
        widget = self._WidgetFactory(self.field, self.request)
        widget.setData(self.content.foo)

        self.assertEqual(widget.applyChanges(self.content), False)
        self.assertEqual(hasattr(self.content, 'foo'), True)
        self.assertEqual(isinstance(self.content.foo, TestContact), True)
        self.assertEqual(self.content.foo.name, u'Foo Name')
        self.assertEqual(self.content.foo.email, u'foo@foo.test')

    def test_new(self):
        request = TestRequest()
        widget = ObjectWidget(self.field, request, TestContact)
        self.assertEquals(int(widget.haveData()), 0)
        check_list = (
            'input', 'name="field.foo.name"',
            'input', 'name="field.foo.email"'
        )
        self.verifyResult(widget(), check_list)

    def test_edit(self):
        request = TestRequest(form={
            'field.foo.name': u'fred',
            'field.foo.email': u'fred@fred.com'
            })
        widget = ObjectWidget(self.field, request, TestContact)
        self.assertEquals(int(widget.haveData()), 1)
        o = widget.getData()
        self.assertEquals(hasattr(o, 'name'), 1)
        self.assertEquals(o.name, u'fred')
        self.assertEquals(o.email, u'fred@fred.com')
        check_list = (
            'input', 'name="field.foo.name"', 'value="fred"',
            'input', 'name="field.foo.email"', 'value="fred@fred.com"',
        )
        self.verifyResult(widget(), check_list)

def test_suite():
    return unittest.makeSuite(ObjectWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

# vim: set filetype=python ts=4 sw=4 et si


