##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""File Widget tests

$Id$
"""
import unittest, doctest

from StringIO import StringIO
from zope.app.form.interfaces import IInputWidget
from zope.app.form.browser import MimeDataWidget

from zope.app.form.browser.tests.test_browserwidget import SimpleInputWidgetTest

from zope.interface.verify import verifyClass

class MimeDataWidgetTest(SimpleInputWidgetTest):
    """Documents and tests the mime widget.
    
        >>> verifyClass(IInputWidget, MimeDataWidget)
        True
    """

    _WidgetFactory = MimeDataWidget

    def setUp(self):
        super(MimeDataWidgetTest, self).setUp()
        file = StringIO('Foo Value')
        file.filename = 'test.txt'
        self._widget.request.form['field.foo'] = file

    def testProperties(self):
        self.assertEqual(self._widget.tag, 'input')
        self.assertEqual(self._widget.type, 'file')
        self.assertEqual(self._widget.cssClass, '')
        self.assertEqual(self._widget.extra, '')
        self.assertEqual(self._widget.default, '')
        self.assertEqual(self._widget.displayWidth, 20)
        self.assertEqual(self._widget.displayMaxWidth, '')

    def testRender(self):
        value = 'Foo Value'
        self._widget.setRenderedValue(value)
        check_list = ('type="file"', 'id="field.foo"', 'name="field.foo"',
                      'size="40"')

        self.verifyResult(self._widget(), check_list)
        check_list = ('type="hidden"',) + check_list[1:-1]
        self.verifyResult(self._widget.hidden(), check_list)
        check_list = ('style="color: red"',) + check_list
        self._widget.extra = 'style="color: red"'
        self.verifyResult(self._widget.hidden(), check_list)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MimeDataWidgetTest),
        doctest.DocTestSuite(),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
