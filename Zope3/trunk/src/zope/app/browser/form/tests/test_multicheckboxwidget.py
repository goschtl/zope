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
$Id: test_multicheckboxwidget.py,v 1.7 2003/06/05 14:23:05 fdrake Exp $
"""
import unittest

from zope.app.browser.form.widget import MultiCheckBoxWidget
from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest

class MultiCheckBoxWidgetTest(BrowserWidgetTest):

    _WidgetFactory = MultiCheckBoxWidget

    def setUp(self):
        BrowserWidgetTest.setUp(self)
        self._widget.context.allowed_values = (u'foo', u'bar')

    def testProperties(self):
        self.assertEqual(self._widget.getValue('cssClass'), "")
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('orientation'), 'vertical')


    def testRenderItem(self):
        check_list = ('type="checkbox"', 'id="field.bar"',
                      'name="field.bar"', 'value="foo"', 'Foo')
        self.verifyResult(
            self._widget.renderItem(0, 'Foo', 'foo', 'field.bar', None),
            check_list)
        check_list += ('checked="checked"',)
        self.verifyResult(
            self._widget.renderSelectedItem(
                0, 'Foo', 'foo', 'field.bar', None),
            check_list)


    def testRenderItems(self):
        check_list = ('type="checkbox"', 'id="field.foo"',
                      'name="field.foo"', 'value="bar"', 'bar',
                      'value="foo"', 'foo', 'checked="checked"')
        self.verifyResult('\n'.join(self._widget.renderItems('bar')),
                          check_list)


    def testRender(self):
        value = 'bar'
        self._widget.setData(value)
        check_list = ('type="checkbox"', 'id="field.foo"',
                      'name="field.foo"', 'value="bar"', 'bar',
                      'value="foo"', 'foo', 'checked="checked"')
        self.verifyResult(self._widget(), check_list)

        check_list = ('type="hidden"', 'id="field.foo"', 'name="field.foo"',
                      'value="bar"')
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)


def test_suite():
    return unittest.makeSuite(MultiCheckBoxWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
