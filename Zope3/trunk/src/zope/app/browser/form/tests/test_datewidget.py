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
$Id: test_datewidget.py,v 1.2 2003/08/13 21:28:04 garrett Exp $
"""
from unittest import main, makeSuite
from zope.app.datetimeutils import parseDatetimetz
from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest
from zope.app.browser.form.widget import DateWidget
from zope.app.interfaces.form import ConversionError, WidgetInputError
from zope.schema import Date


class DateWidgetTest(BrowserWidgetTest):

    _FieldFactory = Date
    _WidgetFactory = DateWidget

    def test_hasInput(self):
        del self._widget.request.form['field.foo']
        self.failIf(self._widget.hasInput())
        self._widget.request.form['field.foo'] = u''
        self.failUnless(self._widget.hasInput())
        self._widget.request.form['field.foo'] = u'2003/03/26'
        self.failUnless(self._widget.hasInput())

    def test_getInputValue(self):
        TEST_DATE= u'2003/03/26'
        self._widget.request.form['field.foo'] = u''
        self.assertRaises(WidgetInputError, self._widget.getInputValue)
        self._widget.request.form['field.foo'] = TEST_DATE
        self.assertEquals(
            self._widget.getInputValue(), 
            parseDatetimetz(TEST_DATE).date())
        self._widget.request.form['field.foo'] = u'abc'
        self.assertRaises(ConversionError, self._widget.getInputValue)


def test_suite():
    return makeSuite(DateWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')

