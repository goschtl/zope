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
$Id: test_multilistwidget.py,v 1.4 2003/02/20 14:45:44 stevea Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.browser.form.widget import MultiListWidget

from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest

class MultiListWidgetTest(BrowserWidgetTest):

    _WidgetFactory = MultiListWidget

    def setUp(self):
        BrowserWidgetTest.setUp(self)
        self._widget.context.allowed_values = (u'foo', u'bar')

    def testProperties(self):
        self.assertEqual(self._widget.getValue('cssClass'), "")
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('size'), 5)


    def testRenderItem(self):
        check_list = ('option', 'value="foo"', 'Foo')
        self._verifyResult(
            self._widget.renderItem(0, 'Foo', 'foo', 'field.bar', None),
            check_list)
        check_list += ('selected="selected"',)
        self._verifyResult(
            self._widget.renderSelectedItem(
                0, 'Foo', 'foo', 'field.bar', None),
            check_list)

    def testRenderItems(self):
        check_list = ('option', 'value="foo"', 'bar',
                      'value="foo"', 'foo', 'selected="selected"')
        self._verifyResult('\n'.join(self._widget.renderItems('foo')),
                           check_list)


    def testRender(self):
        value = 'foo'
        check_list = ('select', 'id="field.foo"', 'name="field.foo"',
                      'size="5"', 'option', 'value="foo"', '>foo<',
                      'value="foo"', '>bar<', 'selected="selected"',
                      'multiple="multiple"')
        self._verifyResult(self._widget.render(value), check_list)

        check_list = ('type="hidden"', 'id="field.foo"', 'name="field.foo"',
                      'value="foo"')
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)



def test_suite():
    return makeSuite(MultiListWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
