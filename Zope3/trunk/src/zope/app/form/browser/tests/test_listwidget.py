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
$Id: test_listwidget.py,v 1.1 2004/03/14 01:11:37 srichter Exp $
"""
import unittest, doctest

from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser.widget import ListWidget
from zope.app.form.browser.tests.test_browserwidget import BrowserWidgetTest
from zope.interface.verify import verifyClass

class ListWidgetTest(BrowserWidgetTest):
    """Documents and tests the list widget.
        
        >>> verifyClass(IInputWidget, ListWidget)
        True
    """

    def setUp(self):
        BrowserWidgetTest.setUp(self)
        self._widget.context.allowed_values = (u'foo', u'bar')

    _WidgetFactory = ListWidget

    def testProperties(self):
        self.assertEqual(self._widget.cssClass, "")
        self.assertEqual(self._widget.extra, '')
        self.assertEqual(self._widget.firstItem, 0)
        self.assertEqual(self._widget.size, 5)


    def testRenderItem(self):
        check_list = ('option', 'value="foo"', 'Foo')
        self.verifyResult(
            self._widget.renderItem(0, 'Foo', 'foo', 'field.bar', None),
            check_list)
        check_list += ('selected="selected"',)
        self.verifyResult(
            self._widget.renderSelectedItem(
                0, 'Foo', 'foo', 'field.bar', None),
            check_list)


    def testRenderItems(self):
        check_list = ('option', 'value="foo"', 'bar',
                      'value="foo"', 'foo', 'selected="selected"')
        self.verifyResult('\n'.join(self._widget.renderItems('foo')),
                          check_list)


    def testRender(self):
        value = 'foo'
        check_list = ('select', 'id="field.foo"', 'name="field.foo"',
                      'size="5"', 'option', 'value="foo"', '>foo<',
                      'value="foo"', '>bar<', 'selected="selected"')
        self._widget.setRenderedValue(value)
        self.verifyResult(self._widget(), check_list)

        check_list = ('type="hidden"', 'id="field.foo"', 'name="field.foo"',
                      'value="foo"')
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)



def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ListWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
