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

$Id: testBrowserWidget.py,v 1.2 2002/07/17 16:54:15 jeremy Exp $
"""
import unittest
from Zope.App.Forms.Views.Browser.Widget import BrowserWidget

class Field:
    """Field Stub """
    id = 'foo'
    

class BrowserWidgetTest(unittest.TestCase):

    def setUp(self):
        field = Field()
        request = {'field_foo': 'Foo Value'}
        self._widget = BrowserWidget(field, request)

    def _verifyResult(self, result, check_list):
        for check in check_list:
            self.assertNotEqual(-1, result.find(check),
                                '"'+check+'" not found in "'+result+'"')

    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'text')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('hidden'), 0)
        self.assertEqual(self._widget.getValue('extra'), '')

    def testRender(self):
        value = 'Foo Value'
        check_list = ('type="text"', 'name="field_foo"', 'value="Foo Value"')
        self._verifyResult(self._widget.render(value), check_list)
        check_list = ('type="hidden"',) + check_list[1:]
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('type="hidden"', 'style="color: red"') + check_list[1:]
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)


def test_suite():
    return unittest.makeSuite(BrowserWidgetTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
