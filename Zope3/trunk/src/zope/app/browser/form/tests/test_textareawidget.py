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
$Id: test_textareawidget.py,v 1.3 2003/01/15 15:44:33 ryzaja Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.browser.form.widget import TextAreaWidget

from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest


class TextAreaWidgetTest(BrowserWidgetTest):

    _WidgetFactory = TextAreaWidget

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'text')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('width'), 60)
        self.assertEqual(self._widget.getValue('height'), 15)

    def testRender(self):
        value = "Foo Value"
        check_list = ('rows="15"', 'cols="60"', 'id="field.foo"',
                      'name="field.foo"', 'textarea')
        self._verifyResult(self._widget.render(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.render(value), check_list)
        check_list = ('type="hidden"', 'id="field.foo"', 'name="field.foo"',
                      'value="Foo Value"')
        self._verifyResult(self._widget.renderHidden(value), check_list)

    def testRow(self):
        self._widget.request.form.clear()
        label = ''.join(self._widget.label().strip().split())
        value = ''.join(self._widget().strip().split())
        row = ''.join(self._widget.row().strip().split())
        self.assertEqual(row,
                         '<tdcolspan="2">%s<br/>%s</td>' % (label, value))



def test_suite():
    return makeSuite(TextAreaWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
