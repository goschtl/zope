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
$Id: test_setPrefix.py,v 1.1 2002/10/29 17:19:48 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Forms.Views.Browser.Widget import TextWidget
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from testBrowserWidget import BrowserWidgetTest
from Zope.Schema import Text


class TextWidgetTest(BrowserWidgetTest):
    
    def setUp(self):
        field = Text(__name__ = 'foo')
        request = TestRequest()
        request.form['spam.foo'] = u'Foo Value'
        self._widget = TextWidget(field, request)
        self._widget.setPrefix('spam')

    def testGetData(self):
        self.assertEqual(self._widget.getData(), u'Foo Value')

    def testRender(self):
        value = 'Foo Value 2'
        check_list = ('type="text"', 'name="spam.foo"', 'value="Foo Value 2"',
                      'size="20"')
        self._widget.setData(value)
        self._verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self._verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.hidden(), check_list)



def test_suite():
    return makeSuite(TextWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
