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
$Id: test_radiowidget.py,v 1.6 2003/04/08 21:34:22 fdrake Exp $
"""
import unittest

from zope.app.browser.form.widget import RadioWidget
from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest

class RadioWidgetTest(BrowserWidgetTest):

    _WidgetFactory = RadioWidget

    def setUp(self):
        BrowserWidgetTest.setUp(self)
        self._widget.context.allowed_values = (u'foo', u'bar')

    def testProperties(self):
        self.assertEqual(self._widget.getValue('cssClass'), "")
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('firstItem'), 0)
        self.assertEqual(self._widget.getValue('orientation'), 'vertical')


    def testRenderItem(self):
        check_list = ('type="radio"', 'id="field.bar.0"',
                      'name="field.bar"', 'value="foo"', 'Foo')
        self._verifyResult(
            self._widget.renderItem(0, 'Foo', 'foo', 'field.bar', None),
            check_list)
        check_list += ('checked="checked"',)
        self._verifyResult(
            self._widget.renderSelectedItem(
                0, 'Foo', 'foo', 'field.bar', None),
            check_list)


    def testRenderItems(self):
        check_list = ('type="radio"', 'id="field.foo.0"', 'name="field.foo"',
                      'value="bar"', 'bar', 'value="foo"', 'foo',
                      'checked="checked"')
        self._verifyResult('\n'.join(self._widget.renderItems('bar')),
                           check_list)


    def testRender(self):
        value = 'bar'
        check_list = ('type="radio"', 'id="field.foo.0"',
                      'name="field.foo"', 'value="bar"', 'bar',
                      'value="foo"', 'foo', 'checked="checked"')
        self._verifyResult(self._widget.render(value), check_list)

        check_list = ('type="hidden"', 'id="field.foo"',
                      'name="field.foo"', 'value="bar"')
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)

    def testLabel(self):
        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label, 'Foo Title')

    def testTranslatedLabel(self):
        import zope.app.browser.form.tests
        from zope.i18n.gettextmessagecatalog import GettextMessageCatalog
        from zope.i18n.globaltranslationservice import translationService
        import os
        path = os.path.dirname(zope.app.browser.form.tests.__file__)
        catalog = GettextMessageCatalog(
            'pl', 'zope',
            os.path.join(path, 'testlabeltranslation.mo'))
        translationService.addCatalog(catalog)

        label = ' '.join(self._widget.label().strip().split())
        self.assertEqual(label, 'oofay itletay')

    def testRow(self):
        self._widget.request.form.clear()
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
    return unittest.makeSuite(RadioWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
