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
$Id: test_multilistwidget.py,v 1.6 2003/05/22 22:50:09 jim Exp $
"""
import unittest

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
        self._widget.setData(value)
        check_list = ('select', 'id="field.foo"', 'name="field.foo"',
                      'size="5"', 'option', 'value="foo"', '>foo<',
                      'value="foo"', '>bar<', 'selected="selected"',
                      'multiple="multiple"')
        self._verifyResult(self._widget(), check_list)

        check_list = ('type="hidden"', 'id="field.foo"', 'name="field.foo"',
                      'value="foo"')
        self._verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self._verifyResult(self._widget.hidden(), check_list)



def test_suite():
    return unittest.makeSuite(MultiListWidgetTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
