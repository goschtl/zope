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
$Id: testCheckBoxWidget.py,v 1.1 2002/07/16 15:15:55 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Forms.Views.Browser.Widget import CheckBoxWidget

from testBrowserWidget import BrowserWidgetTest, Field


class CheckBoxWidgetTest(BrowserWidgetTest):
    
    def setUp(self):
        field = Field()
        request = {'field_foo': 'Foo Value'}
        self._widget = CheckBoxWidget(field, request)

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'checkbox')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('hidden'), 0)
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('default'), 0)

    def testRender(self):
        value = 1
        check_list = ('type="checkbox"', 'name="field_foo"',
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
    return TestSuite((
        makeSuite(CheckBoxWidgetTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
