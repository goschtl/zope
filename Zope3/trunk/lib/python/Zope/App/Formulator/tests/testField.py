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
This test suite tests all Field methods with exception tothe ones defined by
IInstanceFactory, since they have their own test suite.

$Id: testField.py,v 1.2 2002/06/10 23:27:50 jim Exp $
"""

import unittest
from Zope.App.Formulator.Field import Field
from Zope.App.Formulator.Validators.StringValidator import StringValidator

class ContentObject:
    """Content Object stub that will provide the context fir the
       InstanceFactory"""
    pass



class Test( unittest.TestCase ):


    def _makeField(self):
        """Make a field to test the functions with."""

        context = ContentObject()
        some_field = Field(context=context,
                           id='some',
                           title='Something',
                           description='This is some field.',
                           required=1,
                           default='Empty',
                           validator=StringValidator())
        return some_field


    def testInitWithoutContext(self):
        """Test __init__ without passing a context."""
        some_field = Field(id='some',
                           title='Something',
                           description='This is some field.',
                           required=1,
                           default='Empty',
                           validator=None)

        self.assertEqual(some_field.context, None)
        self.assertEqual(some_field.id, 'some')
        self.assertEqual(some_field.title, 'Something')
        self.assertEqual(some_field.description, 'This is some field.')
        self.assertEqual(some_field.required, 1)
        self.assertEqual(some_field.default, 'Empty')
        self.assertEqual(some_field.validator, None)        


    def testInitWithContext(self):
        """Test __init__ with passing a context."""
        context = ContentObject()
        some_field = Field(context=context,
                           id='some',
                           title='Something',
                           description='This is some field.',
                           required=1,
                           default='Empty',
                           validator=None)

        self.assertEqual(some_field.context, context)
        self.assertEqual(some_field.id, 'some')
        self.assertEqual(some_field.title, 'Something')
        self.assertEqual(some_field.description, 'This is some field.')
        self.assertEqual(some_field.required, 1)
        self.assertEqual(some_field.default, 'Empty')
        self.assertEqual(some_field.validator, None)        


    def testGetValidator(self):
        """Test the getValidator method."""
        field = self._makeField()
        self.assertEqual(type(field.getValidator()), type(StringValidator()))        


    def testHasValue(self):
        """Test the hasValue method."""
        field = self._makeField()
        self.assertEqual(field.hasValue('id'), 1)
        self.assertEqual(field.hasValue('foo'), 0)


    def testGetValue(self):
        """Test the getValue method."""
        field = self._makeField()
        self.assertEqual(field.getValue('id'), 'some')
        self.assertEqual(field.getValue('foo'), None)
        self.assertEqual(field.getValue('foo', 'bar'), 'bar')


    def testIsRequired(self):
        """Test the isRequired method."""
        field = self._makeField()
        self.assertEqual(field.isRequired(), 1)


    def testGetErrorNames(self):
        """Test the getErrorNames method."""
        field = self._makeField()
        self.assertEqual(field.getErrorNames(), ['externalValidatorFailed',
                                                 'requiredNotFound', 'tooLong'])

    def testGetErrorMessage(self):
        """Test the getErrorMessage method."""
        field = self._makeField()
        self.assertEqual(field.getErrorMessage('tooLong'), field.validator.tooLong)
        self.assertEqual(field.getErrorMessage('foo'), None)
        


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase( Test )


if __name__=='__main__':
    unittest.TextTestRunner().run( test_suite() )

