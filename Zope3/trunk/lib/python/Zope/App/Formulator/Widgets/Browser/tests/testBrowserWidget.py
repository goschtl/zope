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

$Id: testBrowserWidget.py,v 1.2 2002/06/10 23:27:49 jim Exp $
"""
import unittest
from Zope.App.Formulator import Errors


class ContentObject:
    """Class to provide a stub for a field"""

    def getFoo(self):
        """ """
        return "Foo Value"
    

class Field:
    """Field Stub """

    id = 'foo'

    def __init__(self, context):
        """ """
        self._context  = context


    def getPropertyInContext(self):
        """ """
        return self._context.getFoo()
    
    


class Test(unittest.TestCase):


    def setUp(self):

        from Zope.App.Formulator.Widgets.Browser import BrowserWidget
        obj = ContentObject()
        field = Field(obj)
        self._widget = BrowserWidget.BrowserWidget(field)


    def testProperties(self):

        self.assertEqual(self._widget.getValue('tag'), 'input')
        self.assertEqual(self._widget.getValue('type'), 'text')
        self.assertEqual(self._widget.getValue('cssClass'), '')
        self.assertEqual(self._widget.getValue('hidden'), 0)
        self.assertEqual(self._widget.getValue('extra'), '')


    def testRendering(self):


        request = {'field_foo': 'Foo Value'}

        self.assertEqual(self._widget.render(request),
                         '<input type="text" name="field_foo" '
                         'value="Foo Value"  />')

        self.assertEqual(self._widget.render_hidden(request),
                         '<input type="hidden" name="field_foo" '
                         'value="Foo Value"  />')

        self._widget.extra = '''style="color: red"'''
        self.assertEqual(self._widget.render_hidden(request),
                         '<input type="hidden" name="field_foo" '
                         'value="Foo Value" style="color: red" />')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )





