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
$Id: test_checkboxwidget.py,v 1.2 2002/12/25 14:12:32 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.browser.form.widget import CheckBoxWidget

from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest


class CheckBoxWidgetTest(BrowserWidgetTest):

    _WidgetFactory = CheckBoxWidget

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'checkbox')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('default'), 0)

    def testRender(self):
        value = 1
        check_list = ('type="checkbox"', 'name="field.foo"',
                      'checked="checked"')
        self._verifyResult(self._widget.render(value), check_list)
        value = 0
        check_list = check_list[:-1]
        self._verifyResult(self._widget.render(value), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)



def test_suite():
    return makeSuite(CheckBoxWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
