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
$Id: test_intwidget.py,v 1.1 2003/01/20 16:23:38 mgedmin Exp $
"""
from unittest import main, makeSuite
from zope.app.browser.form.tests.test_browserwidget import BrowserWidgetTest
from zope.app.browser.form.widget import IntWidget
from zope.app.interfaces.form import ConversionError
from zope.schema import Int


class IntWidgetTest(BrowserWidgetTest):

    _FieldFactory = Int
    _WidgetFactory = IntWidget

    def test_haveData(self):
        del self._widget.request.form['field.foo']
        self.failIf(self._widget.haveData())
        self._widget.request.form['field.foo'] = u''
        self.failIf(self._widget.haveData())
        self._widget.request.form['field.foo'] = u'123'
        self.failUnless(self._widget.haveData())

    def test_getData(self):
        self._widget.request.form['field.foo'] = u''
        self.assertEquals(self._widget.getData(optional=1), None)
        self._widget.request.form['field.foo'] = u'123'
        self.assertEquals(self._widget.getData(), 123)
        self._widget.request.form['field.foo'] = u'abc'
        self.assertRaises(ConversionError, self._widget.getData)


def test_suite():
    return makeSuite(IntWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
