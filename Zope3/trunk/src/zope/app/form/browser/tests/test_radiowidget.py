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
$Id: test_radiowidget.py,v 1.1 2004/03/14 01:11:37 srichter Exp $
"""
import os
import unittest, doctest
from zope.interface.verify import verifyClass

from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
from zope.i18n.translationdomain import TranslationDomain

from zope.app.tests import ztapi
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.widget import RadioWidget
from zope.app.form.browser.tests.test_browserwidget import BrowserWidgetTest
import zope.app.form.browser.tests

class RadioWidgetTest(BrowserWidgetTest):
    """Documents and tests the radio widget.
        
        >>> verifyClass(IInputWidget, RadioWidget)
        True
    """

    _WidgetFactory = RadioWidget

    def setUp(self):
        BrowserWidgetTest.setUp(self)
        self._widget.context.allowed_values = (u'foo', u'bar')

    def testProperties(self):
        self.assertEqual(self._widget.cssClass, "")
        self.assertEqual(self._widget.extra, '')
        self.assertEqual(self._widget.firstItem, 0)
        self.assertEqual(self._widget.orientation, 'vertical')


    def testRenderItem(self):
        check_list = ('type="radio"', 'id="field.bar.0"',
                      'name="field.bar"', 'value="foo"', 'Foo')
        self.verifyResult(
            self._widget.renderItem(0, 'Foo', 'foo', 'field.bar', None),
            check_list)
        check_list += ('checked="checked"',)
        self.verifyResult(
            self._widget.renderSelectedItem(
                0, 'Foo', 'foo', 'field.bar', None),
            check_list)


    def testRenderItems(self):
        check_list = ('type="radio"', 'id="field.foo.0"', 'name="field.foo"',
                      'value="bar"', 'bar', 'value="foo"', 'foo',
                      'checked="checked"')
        self.verifyResult('\n'.join(self._widget.renderItems('bar')),
                          check_list)


    def testRender(self):
        value = 'bar'
        self._widget.setRenderedValue(value)
        check_list = ('type="radio"', 'id="field.foo.0"',
                      'name="field.foo"', 'value="bar"', 'bar',
                      'value="foo"', 'foo', 'checked="checked"')
        self.verifyResult(self._widget(), check_list)

        check_list = ('type="hidden"', 'id="field.foo"',
                      'name="field.foo"', 'value="bar"')
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)

    def testLabel(self):
        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label, 'Foo Title')

    def testTranslatedLabel(self):
        path = os.path.dirname(zope.app.form.browser.tests.__file__)
        catalog = GettextMessageCatalog(
            'pl', 'zope', os.path.join(path, 'testlabeltranslation.mo'))
        domain = TranslationDomain('zope')
        domain.addCatalog(catalog)
        ztapi.provideUtility(ITranslationDomain, domain, 'zope')
        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label, 'oofay itletay')

    def testRowRequired(self):
        self._widget.request.form.clear()
        self._widget.context.required = True
        label = ''.join(self._widget.label().strip().split())
        value = ''.join(self._widget().strip().split())
        row = ''.join(self._widget.row().strip().split())
        id = 'field.foo'
        self.assertEqual(row, '<divclass="labelrequired">'
                              '<labelfor="%s">%s</label>'
                              '</div>'
                              '<divclass="field"id="%s">'
                              '%s'
                              '</div>' % (id, label, id, value))

    def testRowNonRequired(self):
        self._widget.request.form.clear()
        self._widget.context.required = False
        label = ''.join(self._widget.label().strip().split())
        value = ''.join(self._widget().strip().split())
        row = ''.join(self._widget.row().strip().split())
        id = 'field.foo'
        self.assertEqual(row, '<divclass="label">'
                              '<labelfor="%s">%s</label>'
                              '</div>'
                              '<divclass="field"id="%s">'
                              '%s'
                              '</div>' % (id, label, id, value))

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(RadioWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
