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
$Id: test_textareawidget.py,v 1.9 2003/08/16 17:23:37 sidnei Exp $
"""
import unittest

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
        self._widget.setRenderedValue(value)
        check_list = ('rows="15"', 'cols="60"', 'id="field.foo"',
                      'name="field.foo"', 'textarea')
        self.verifyResult(self._widget(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"', 'id="field.foo"', 'name="field.foo"',
                      'value="Foo Value"')
        self.verifyResult(self._widget.hidden(), check_list)


def test_suite():
    return unittest.makeSuite(TextAreaWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
