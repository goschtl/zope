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
$Id: test_passwordwidget.py,v 1.5 2003/04/08 21:34:22 fdrake Exp $
"""
import unittest

from zope.app.browser.form.widget import PasswordWidget
from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest


class PasswordWidgetTest(BrowserWidgetTest):

    _WidgetFactory = PasswordWidget

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'password')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('default'), '')
        self.assertEqual(self._widget.getValue('displayWidth'), 20)
        self.assertEqual(self._widget.getValue('displayMaxWidth'), '')

    def testRender(self):
        value = 'Foo Value'
        check_list = ('type="password"', 'id="field.foo"',
                      'name="field.foo"', 'value=""', 'size="20"')
        self._verifyResult(self._widget.render(value), check_list)

    def testHidden(self):
        self.assertRaises(NotImplementedError, self._widget.hidden)

def test_suite():
    return unittest.makeSuite(PasswordWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
