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

$Id: test_widget_deprecations.py,v 1.1 2003/08/13 21:28:04 garrett Exp $
"""
import unittest
import random

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.browser.form.widget import BrowserWidget
from zope.app.form import widget
from zope.app.browser.form import widget as browserwidget
from zope.publisher.browser import TestRequest
from zope.schema import Text


class OldWidget(BrowserWidget):
    """Simulates a typical browser widget before the renaming of:
    
        getData -> getInputValue
        setData -> setRenderedValue
        haveData -> hasInput
    """

    def __init__(self, context, request):
        super(OldWidget, self).__init__(context, request)
        self._data = random.random() > 0.5 and u'foo' or None

    def haveData(self):
        return self._data is None

    def getData(self):
        return self._data


warnings = []

def warn(*args, **wk):
    warnings.append(args[1]) # append the exception class


class TestOldWidget(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self._widget = OldWidget(Text(__name__='test'), TestRequest())
        widget.warn = warn
        browserwidget.warn = warn
        global warnings
        warnings = []

    def test_haveInput(self):
        self.assertEqual(self._widget.haveData(), self._widget.hasInput())
    
    def test_getData(self):
        self.assertEqual(self._widget.getData(), self._widget.getInputValue())
    
    def test_setData(self):
        self.assertEqual(len(warnings), 0)
        self._widget.setData(u'bar')
        self.assertEqual(self._widget.getInputValue(), u'bar')
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0], DeprecationWarning)


class TestCurrentWidget(PlacelessSetup, unittest.TestCase):

    _WidgetFactory = BrowserWidget

    def setUp(self):
        PlacelessSetup.setUp(self)
        self._widget = BrowserWidget(Text(__name__='test'), TestRequest())
        widget.warn = warn
        browserwidget.warn = warn
        global warnings
        warnings = []

    def test_haveInput(self):
        self.assertEqual(len(warnings), 0)
        self.failIf(self._widget.haveData())
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0], DeprecationWarning)
    
    def test_getData(self):
        self._widget.request.form['field.test'] = u'foo'
        self.assertEqual(len(warnings), 0)
        self.assertEqual(self._widget.getData(), u'foo')
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0], DeprecationWarning)

    def test_setData(self):
        self.assertEqual(len(warnings), 0)
        self._widget.setData('foo')
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0], DeprecationWarning)

        
def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestOldWidget),
        unittest.makeSuite(TestCurrentWidget)))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')

