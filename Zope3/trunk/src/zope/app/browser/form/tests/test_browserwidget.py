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

$Id: test_browserwidget.py,v 1.18 2004/01/20 18:56:31 garrett Exp $
"""

from zope.interface import Interface, implements
from zope.app.browser.form.widget import BrowserWidget
from zope.app.interfaces.form import ConversionError
from zope.app.interfaces.form import WidgetInputError, MissingInputError
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.globaltranslationservice import translationService
from zope.publisher.browser import TestRequest
from zope.schema import Text
import os
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app.browser.form.tests import support
import zope.app.browser.form.tests

class BrowserWidgetTest(PlacelessSetup,
                        support.VerifyResults,
                        unittest.TestCase):
    _FieldFactory = Text
    _WidgetFactory = BrowserWidget

    def setUpContent(self, desc=u''):
        class ITestContent(Interface):
            foo = self._FieldFactory(
                    title = u"Foo Title",
                    description = desc,
                    )
        class TestObject:
            implements(ITestContent)

        self.content = TestObject()
        field = ITestContent['foo']
        request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl')
        request.form['field.foo'] = u'Foo Value'
        self._widget = self._WidgetFactory(field, request)

    def setUp(self):
        super(BrowserWidgetTest, self).setUp()
        self.setUpContent()

    def test_required(self):
        self._widget.context.required = False
        self.failIf(self._widget.required)
        self._widget.context.required = True
        self.failUnless(self._widget.required)

    def test_hasInput(self):
        self.failUnless(self._widget.hasInput())
        del self._widget.request.form['field.foo']
        self.failIf(self._widget.hasInput())

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'text')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('extra'), '')

    def testRender(self):
        value = 'Foo Value'
        check_list = ('type="text"', 'id="field.foo"', 'name="field.foo"',
                      'value="Foo Value"')
        self._widget.setRenderedValue(value)
        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:]
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('type="hidden"', 'style="color: red"') + check_list[1:]
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)

    def testLabel(self):
        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label, '<label for="field.foo">Foo Title</label>')

        self.setUpContent(desc=u"Foo Description")
        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label,
                '<label for="field.foo">'
                '<span title="Foo Description">Foo Title</span></label>'
                )

    def testDescription(self):
        self.setUpContent(desc=u'Foo Description')
        description = ' '.join(self._widget.description.strip().split())
        self.assertEqual(description, u'Foo Description')

    def testTranslatedLabel(self):
        path = os.path.dirname(zope.app.browser.form.tests.__file__)
        catalog = GettextMessageCatalog(
            'pl', 'zope',
            os.path.join(path, 'testlabeltranslation.mo'))
        translationService.addCatalog(catalog)

        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label, '<label for="field.foo">oofay itletay</label>')

    def testRowRequired(self):
        self._widget.request.form.clear()
        self._widget.context.required = True
        label = ''.join(self._widget.label().strip().split())
        value = ''.join(self._widget().strip().split())
        row = ''.join(self._widget.row().strip().split())
        self.assertEqual(row, '<divclass="labelrequired">%s</div>'
                              '<divclass="field">%s</div>' % (label, value))

    def testRowNonRequired(self):
        self._widget.request.form.clear()
        self._widget.context.required = False
        label = ''.join(self._widget.label().strip().split())
        value = ''.join(self._widget().strip().split())
        row = ''.join(self._widget.row().strip().split())
        self.assertEqual(row, '<divclass="label">%s</div>'
                              '<divclass="field">%s</div>' % (label, value))

class TestWidget(BrowserWidget):

    def _convert(self, v):
        if v == u'barf!':
            raise ConversionError('ralph')
        return v or None

class Test(BrowserWidgetTest):

    _WidgetFactory = TestWidget

    def test_showData(self):

        class W(BrowserWidget):
            def _convert(self, v):
                return u'X' + (v or '')

            def _unconvert(self, v):
                return v and v[1:] or ''

        field = Text(__name__ = 'foo', title = u"Foo Title")
        request = TestRequest()

        w = W(field, request)
        self.assertEqual(w._showData(), '')
        request.form['field.foo'] = 'val'
        self.assertEqual(w._showData(), 'val')

        w.setRenderedValue('Xfoo')
        self.assertEqual(w._showData(), 'foo')

    def test_hasValidInput(self):
        self.assertEqual(self._widget.getInputValue(), u'Foo Value')

        self._widget.request.form['field.foo'] = (1, 2)
        self.failIf(self._widget.hasValidInput())

        self._widget.request.form['field.foo'] = u'barf!'
        self.failIf(self._widget.hasValidInput())

        del self._widget.request.form['field.foo']        
        self._widget.context.required = True
        self.failIf(self._widget.hasValidInput())

        self._widget.context.required = False
        self._widget.request.form['field.foo'] = u''
        self.failUnless(self._widget.hasValidInput())

    def test_getInputValue(self):
        self.assertEqual(self._widget.getInputValue(), u'Foo Value')

        self._widget.request.form['field.foo'] = (1, 2)
        self.assertRaises(WidgetInputError, self._widget.getInputValue)

        self._widget.request.form['field.foo'] = u'barf!'
        self.assertRaises(ConversionError, self._widget.getInputValue)

        del self._widget.request.form['field.foo']        
        self._widget.context.required = True
        self.assertRaises(MissingInputError, self._widget.getInputValue)

        self._widget.context.required = False
        self._widget.request.form['field.foo'] = u''
        self.assertEqual(self._widget.getInputValue(), None)

    def test_applyChanges(self):
        self.assertEqual(self._widget.applyChanges(self.content), True)

    def test_hasInput(self):
        self.failUnless(self._widget.hasInput())
        del self._widget.request.form['field.foo']
        self.failIf(self._widget.hasInput())
        self._widget.request.form['field.foo'] = u'foo'
        self.failUnless(self._widget.hasInput())
        # widget has input, even if input is an empty string
        self._widget.request.form['field.foo'] = u''
        self.failUnless(self._widget.hasInput())

    def test_showData_w_default(self):
        field = Text(__name__ = 'foo', title = u"Foo Title", default=u"def")
        request = TestRequest()
        widget = self._WidgetFactory(field, request)
        self.assertEqual(widget._showData(), u'def')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    suite.addTest(DocTestSuite("zope.app.browser.form.widget"))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
