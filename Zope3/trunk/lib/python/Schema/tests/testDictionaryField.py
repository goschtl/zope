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
$Id: testDictionaryField.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from unittest import TestSuite, main, makeSuite
from Schema import Dictionary, Integer, Float, ErrorNames
from testField import FieldTest

class DictionaryTest(FieldTest):
    """Test the Dictionary Field."""

    def testValidate(self):
        field = Dictionary(id="field", title='Dictionary field',
                           description='', readonly=0, required=0)
        self.assertEqual(None, field.validate(None))
        self.assertEqual( {} , field.validate({}))
        self.assertEqual( {1: 'foo'} , field.validate( {1: 'foo'} ))
        self.assertEqual( {'a': 1} , field.validate( {'a': 1} ))

    def testValidateRequired(self):
        field = Dictionary(id="field", title='Dictionary field',
                           description='', readonly=0, required=1)
        self.assertEqual( {} , field.validate({}))
        self.assertEqual( {1: 'foo'} , field.validate( {1: 'foo'} ))
        self.assertEqual( {'a': 1} , field.validate( {'a': 1} ))
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testValidateMinValues(self):
        field = Dictionary(id="field", title='Dictionary field',
                           description='', readonly=0, required=0,
                           min_values=1)
        self.assertEqual(None, field.validate(None))
        self.assertEqual( {1: 'a'}, field.validate( {1: 'a'} ))
        self.assertEqual( {1: 'a', 2: 'b'}, field.validate( {1: 'a', 2: 'b'} ))
        self.assertRaisesErrorNames(ErrorNames.NotEnoughElements,
                                    field.validate, {})

    def testValidateMaxValues(self):
        field = Dictionary(id="field", title='Dictionary field',
                           description='', readonly=0, required=0,
                           max_values=1)
        self.assertEqual(None, field.validate(None))
        self.assertEqual( {}, field.validate( {} ))
        self.assertEqual( {1: 'a'}, field.validate( {1: 'a'} ))
        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, {1: 'a', 2: 'b'})
        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, {1: 'a', 2: 'b', 3: 'c'})

    def testValidateMinValuesAndMaxValues(self):
        field = Dictionary(id="field", title='Dictionary field',
                           description='', readonly=0, required=0,
                           min_values=1, max_values=2)
        self.assertEqual(None, field.validate(None))
        self.assertEqual( {1: 'a'}, field.validate( {1: 'a'} ))
        self.assertEqual( {1: 'a', 2: 'b'}, field.validate( {1: 'a', 2: 'b'} ))
        self.assertRaisesErrorNames(ErrorNames.NotEnoughElements,
                                    field.validate, {})
        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, {1: 'a', 2: 'b', 3: 'c'})

    def testValidateValueTypes(self):
        field = Dictionary(id="field", title='Dictionary field',
                           description='', readonly=0, required=0,
                           value_types=(Integer, Float))
        self.assertEqual(None, field.validate(None))
        self.assertEqual({'a': 5.3} , field.validate({'a': 5.3}))
        self.assertEqual({'a': 2, 'b': 2.3},
                          field.validate( {'a': 2, 'b': 2.3} ))
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, {1: ''} )
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, {'a': ()} )

    def testValidateKeyTypes(self):
        field = Dictionary(id="field", title='Dictionary field',
                           description='', readonly=0, required=0,
                           key_types=(Integer, Float))
        self.assertEqual(None, field.validate(None))
        self.assertEqual({5.3: 'a'} , field.validate({5.3: 'a'}))
        self.assertEqual({2: 'a', 2.3: 'b'},
                          field.validate( {2: 'a', 2.3: 'b'} ))
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, {'': 1} )
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, {(): 'a'} )


def test_suite():
    return TestSuite((
        makeSuite(DictionaryTest),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
