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
$Id: testListWidget.py,v 1.3 2002/07/24 10:53:48 srichter Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Forms.Views.Browser.Widget import ListWidget

from testBrowserWidget import BrowserWidgetTest

class Field:
    """Field Stub """
    id = 'foo'
    items = [('foo', 'Foo'), ('bar', 'Bar')]

    def get(self, name):
        return getattr(self, name)

class ListWidgetTest(BrowserWidgetTest):
    
    def setUp(self):
        field = Field()
        request = {'field_foo': 'Foo Value'}
        self._widget = ListWidget(field, request)

    def testProperties(self):
        self.assertEqual(self._widget.getValue('cssClass'), "")
        self.assertEqual(self._widget.getValue('hidden'), 0)
        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('items'), [])
        self.assertEqual(self._widget.getValue('firstItem'), 0)
        self.assertEqual(self._widget.getValue('size'), 5)


    def testRenderItem(self):
        check_list = ('option', 'value="foo"', 'Foo')
        self._verifyResult(self._widget.renderItem('Foo', 'foo', 'bar', None),
                           check_list)
        check_list += ('selected="selected"',)
        self._verifyResult(
            self._widget.renderSelectedItem('Foo', 'foo', 'bar', None),
            check_list)


    def testRenderItems(self):
        check_list = ('option', 'value="foo"', 'Bar',
                      'value="foo"', 'Foo', 'selected="selected"')
        self._verifyResult('\n'.join(self._widget.renderItems('foo')),
                           check_list)


    def testRender(self):
        value = 'foo'
        check_list = ('select', 'name="field_foo"', 'size="5"', 
                      'option', 'value="foo"', '>Foo<',
                      'value="foo"', '>Bar<', 'selected="selected"')
        self._verifyResult(self._widget.render(value), check_list)

        check_list = ('type="hidden"', 'name="field_foo"', 'value="foo"')
        self._verifyResult(self._widget.renderHidden(value), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.renderHidden(value), check_list)



def test_suite():
    return makeSuite(ListWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
