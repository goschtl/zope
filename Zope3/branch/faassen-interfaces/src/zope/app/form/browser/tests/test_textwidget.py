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
$Id: test_textwidget.py,v 1.3 2004/05/11 11:17:36 garrett Exp $
"""
import unittest, doctest

from zope.interface.verify import verifyClass
from zope.schema import TextLine

from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser import TextWidget
from zope.app.form.browser.tests.test_browserwidget import SimpleInputWidgetTest

class TextWidgetTest(SimpleInputWidgetTest):
    """Documents and tests the text widget.

        >>> verifyClass(IInputWidget, TextWidget)
        True
    """

    _WidgetFactory = TextWidget

    def testProperties(self):
        self.assertEqual(self._widget.tag, 'input')
        self.assertEqual(self._widget.type, 'text')
        self.assertEqual(self._widget.cssClass, '')
        self.assertEqual(self._widget.extra, '')
        self.assertEqual(self._widget.default, '')
        self.assertEqual(self._widget.displayWidth, 20)
        self.assertEqual(self._widget.displayMaxWidth, '')

    def testRender(self):
        value = 'Foo Value'
        self._widget.setRenderedValue(value)
        check_list = ('type="text"', 'id="field.foo"', 'name="field.foo"',
                      'value="Foo Value"', 'size="20"')
        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TextWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
