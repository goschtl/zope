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
$Id: testTextAreaWidget.py,v 1.1 2002/07/16 15:15:55 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Forms.Views.Browser.Widget import TextAreaWidget

from testBrowserWidget import BrowserWidgetTest, Field


class TextAreaWidgetTest(BrowserWidgetTest):
    
    def setUp(self):
        field = Field()
        request = {'field_foo': 'Foo Value'}
        self._widget = TextAreaWidget(field, request)

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'text')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('hidden'), 0)
        self.assertEqual(self._widget.getValue('extra'), '')
        # self.assertEqual(self._widget.getValue('default'), "")
        self.assertEqual(self._widget.getValue('width'), 80)
        self.assertEqual(self._widget.getValue('height'), 15)

    def testRender(self):
        value = "Foo Value"
        check_list = ('rows="15"', 'cols="80"', 'name="field_foo"', 'textarea')
        self._verifyResult(self._widget.render(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.render(value), check_list)
        check_list = ('type="hidden"', 'name="field_foo"', 'value="Foo Value"')
        self._verifyResult(self._widget.renderHidden(value), check_list)



def test_suite():
    return TestSuite((
        makeSuite(TextAreaWidgetTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
