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

$Id: test_browserwidget.py,v 1.10 2003/04/04 15:39:29 stevea Exp $
"""

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
import zope.app.browser.form.tests

class BrowserWidgetTest(PlacelessSetup, unittest.TestCase):

    _FieldFactory = Text
    _WidgetFactory = BrowserWidget

    def setUp(self):
        PlacelessSetup.setUp(self)
        field = self._FieldFactory(__name__ = 'foo', title = u"Foo Title")
        request = TestRequest(HTTP_ACCEPT_LANGUAGE='pl')
        request.form['field.foo'] = u'Foo Value'
        self._widget = self._WidgetFactory(field, request)

    def _verifyResult(self, result, check_list):
        for check in check_list:
            self.assertNotEqual(-1, result.find(check),
                                '"'+check+'" not found in "'+result+'"')

    def test_required(self):
        self._widget.context.required = False
        self.failIf(self._widget.required)
        self._widget.context.required = True
        self.failUnless(self._widget.required)

    def test_haveData(self):
        self.failUnless(self._widget.haveData())
        del self._widget.request.form['field.foo']
        self.failIf(self._widget.haveData())

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'text')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('extra'), '')

    def testRender(self):
        value = 'Foo Value'
        check_list = ('type="text"', 'id="field.foo"', 'name="field.foo"',
                      'value="Foo Value"')
        self._verifyResult(self._widget.render(value), check_list)
        check_list = ('type="hidden"',) + check_list[1:]
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('type="hidden"', 'style="color: red"') + check_list[1:]
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)

    def testLabel(self):
        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label, '<label for="field.foo">Foo Title</label>')

    def testTranslatedLabel(self):
        path = os.path.dirname(zope.app.browser.form.tests.__file__)
        catalog = GettextMessageCatalog(
            'pl', 'zope',
            os.path.join(path, 'testlabeltranslation.mo'))
        translationService.addCatalog(catalog)

        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label, '<label for="field.foo">oofay itletay</label>')

    def testRow(self):
        self._widget.request.form.clear()
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

        w.setData('Xfoo')
        self.assertEqual(w._showData(), 'foo')

    def test_getData(self):
        self.assertEqual(self._widget.getData(), u'Foo Value')

        self._widget.request.form['field.foo'] = (1, 2)
        self.assertRaises(WidgetInputError, self._widget.getData)

        self._widget.request.form['field.foo'] = u'barf!'
        self.assertRaises(ConversionError, self._widget.getData)

        del self._widget.request.form['field.foo']        
        self._widget.context.required = True
        self.assertEqual(self._widget.getData(optional=1), None)
        self.assertRaises(MissingInputError, self._widget.getData)

        self._widget.context.required = False
        self.assertEqual(self._widget.getData(optional=1), None)
        self.assertEqual(self._widget.getData(), None)


    def test_haveData(self):
        self.failUnless(self._widget.haveData())
        del self._widget.request.form['field.foo']
        self.failIf(self._widget.haveData())
        self._widget.request.form['field.foo'] = u''
        self.failIf(self._widget.haveData())

    def test_showData_w_default(self):
        field = Text(__name__ = 'foo', title = u"Foo Title", default=u"def")
        request = TestRequest()
        widget = self._WidgetFactory(field, request)
        self.assertEqual(widget._showData(), u'def')


def test_suite():
    return unittest.makeSuite(Test)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
