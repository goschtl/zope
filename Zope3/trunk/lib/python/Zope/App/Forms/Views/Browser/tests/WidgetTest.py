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
$Id: WidgetTest.py,v 1.3 2002/09/04 13:44:24 faassen Exp $
"""
import unittest
from Zope.App.Forms.Views.Browser.Widget import BrowserWidget

class ContentObject:
    """Class to provide a stub for a field"""
    foo = "Foo Value"
    

class Field:
    """Field Stub """
    def __init__(self, context):
        self._context  = context

    def getPropertyInContext(self):
        return self._context.getFoo()

    def getValue(self, name):
        return getattr(self, name, None)


class WidgetTest(unittest.TestCase):

    def _getWidget(self, field):
        return BrowserWidget(field)

    def setUp(self):
        obj = ContentObject()
        field = Field(obj)
        self._widget = self._getWidget(field)


    def testProperties(self):
        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'text')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('hidden'), 0)
        self.assertEqual(self._widget.getValue('extra'), '')


    def testRendering(self):
        request = {'field_foo': 'Foo Value'}

        result1 = '<input type="text" name="field_foo" value="Foo Value"  />'
        self.assertEqual(result1, self._widget.render(request))

        result2 = '<input type="hidden" name="field_foo" value="Foo Value"  />'
        self.assertEqual(result2, self._widget.render_hidden(request))

        self._widget.extra = '''style="color: red"'''
        result3 = ('<input type="hidden" name="field_foo" '
                   'value="Foo Value" style="color: red" />')
        self.assertEqual(result3, self._widget.render_hidden(request))


def test_suite():
    return makeSuite(TextWidgetTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
