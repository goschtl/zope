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
$Id: test_checkboxwidget.py,v 1.8 2003/06/05 14:23:05 fdrake Exp $
"""
import unittest

from zope.app.browser.form.widget import CheckBoxWidget
from zope.schema import Bool

from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest


class CheckBoxWidgetTest(BrowserWidgetTest):

    _FieldFactory = Bool
    _WidgetFactory = CheckBoxWidget

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'checkbox')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('default'), 0)

    def testRender(self):
        value = 1
        self._widget.setData(value)
        check_list = ('type="checkbox"', 'id="field.foo"',
                      'name="field.foo"', 'checked="checked"')
        self.verifyResult(self._widget(), check_list)
        value = 0
        self._widget.setData(value)
        check_list = check_list[:-1]
        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)

    def test_getData(self):
        self._widget.request.form['field.foo'] = 'on'
        self.assertEqual(self._widget.getData(), True)
        self._widget.request.form['field.foo'] = 'positive'
        self.assertEqual(self._widget.getData(), False)
        del self._widget.request.form['field.foo']
        self.assertEqual(self._widget.getData(), False)


def test_suite():
    return unittest.makeSuite(CheckBoxWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
