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
$Id: test_multicheckboxwidget.py,v 1.4 2003/02/20 14:45:44 stevea Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
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
        self._verifyResult(
            self._widget.renderItem(0, 'Foo', 'foo', 'field.bar', None),
            check_list)
        check_list += ('checked="checked"',)
        self._verifyResult(
            self._widget.renderSelectedItem(
                0, 'Foo', 'foo', 'field.bar', None),
            check_list)


    def testRenderItems(self):
        check_list = ('type="checkbox"', 'id="field.foo"',
                      'name="field.foo"', 'value="bar"', 'bar',
                      'value="foo"', 'foo', 'checked="checked"')
        self._verifyResult('\n'.join(self._widget.renderItems('bar')),
                           check_list)


    def testRender(self):
        value = 'bar'
        check_list = ('type="checkbox"', 'id="field.foo"',
                      'name="field.foo"', 'value="bar"', 'bar',
                      'value="foo"', 'foo', 'checked="checked"')
        self._verifyResult(self._widget.render(value), check_list)

        check_list = ('type="hidden"', 'id="field.foo"', 'name="field.foo"',
                      'value="bar"')
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)


def test_suite():
    return makeSuite(MultiCheckBoxWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
