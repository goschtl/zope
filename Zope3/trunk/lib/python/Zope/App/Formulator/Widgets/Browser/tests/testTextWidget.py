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


    def getValue(self, name):
        """ """
        return getattr(self, name, None)
    


class Test(unittest.TestCase):


    def setUp(self):

        from Zope.App.Formulator.Widgets.Browser import TextWidget
        content = ContentObject()
        field = Field(content)
        self._widget = TextWidget.TextWidget(field)


    def testProperties(self):

        self.assertEqual(self._widget.getValue('extra'), '')
        self.assertEqual(self._widget.getValue('default'), '')
        self.assertEqual(self._widget.getValue('displayWidth'), 20)
        self.assertEqual(self._widget.getValue('displayMaxWidth'), '')


    def testRendering(self):

        request = {'field_foo': 'Foo Value'}

        self.assertNotEqual(self._widget.render(request), '')

        self.assertNotEqual(self._widget.render_hidden(request), '')

        self._widget.extra = '''style="color: red"'''
        self.assertNotEqual(self._widget.render_hidden(request), '')



def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )

if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )





