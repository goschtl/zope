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
$Id: testMultiCheckboxWidget.py,v 1.1 2002/07/16 15:15:55 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Forms.Views.Browser.Widget import MultiCheckBoxWidget

from testBrowserWidget import BrowserWidgetTest

class Field:
    """Field Stub """
    id = 'foo'
    items = [('Foo', 'foo1'), ('Bar', 'bar1')]

    def get(self, name):
        return getattr(self, name)


class MultiCheckBoxWidgetTest(BrowserWidgetTest):
    
    def setUp(self):
        field = Field()
        request = {'field_foo': 'Foo Value'}
        self._widget = MultiCheckBoxWidget(field, request)

    def testProperties(self):
        self.assertEqual(self._widget.getValue('cssClass'), "")
        self.assertEqual(self._widget.getValue('hidden'), 0)
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('items'), [])
        self.assertEqual(self._widget.getValue('orientation'), 'vertical')


    def testRenderItem(self):
        check_list = ('type="checkbox"', 'name="field_bar"', 'value="foo"',
                      'Foo')
        self._verifyResult(self._widget.renderItem('Foo', 'foo', 'bar', None),
                           check_list)
        check_list += ('checked="checked"',)
        self._verifyResult(
            self._widget.renderSelectedItem('Foo', 'foo', 'bar', None),
            check_list)


    def testRenderItems(self):
        check_list = ('type="checkbox"', 'name="field_foo"', 'value="bar1"',
                      'Bar', 'value="foo1"', 'Foo', 'checked="checked"')
        self._verifyResult('\n'.join(self._widget.renderItems('bar1')),
                           check_list)


    def testRender(self):
        value = 'bar1'
        check_list = ('type="checkbox"', 'name="field_foo"', 'value="bar1"',
                      'Bar', 'value="foo1"', 'Foo', 'checked="checked"')
        self._verifyResult(self._widget.render(value), check_list)

        check_list = ('type="hidden"', 'name="field_foo"', 'value="bar1"')
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)


def test_suite():
    return TestSuite((
        makeSuite(MultiCheckBoxWidgetTest),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
