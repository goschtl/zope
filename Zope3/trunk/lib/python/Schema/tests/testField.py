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

$Id: testField.py,v 1.1 2002/06/24 08:31:48 faassen Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Schema.Exceptions import StopValidation, ValidationError

from Schema import Field, Int, Str, Bool
from Schema import IField

class FieldTestCase(TestCase):
    def test_validate(self):
        field = Field(
            title='Not required field',
            description='',
            readonly=0,
            required=0)
        self.assertEquals(None, field.validate(None))
        self.assertEquals('foo', field.validate('foo'))
        self.assertEquals(1, field.validate(1))
        self.assertEquals(0, field.validate(0))
        self.assertEquals('', field.validate(''))
        
    def test_validate_required(self):
        field = Field(
            title='Required field',
            description='',
            readonly=0,
            required=1)
        self.assertRaises(ValidationError, field.validate, None)
        self.assertEquals('foo', field.validate('foo'))
        self.assertEquals(1, field.validate(1))
        self.assertEquals(0, field.validate(0))
        self.assertEquals('', field.validate(''))
        
class StrTestCase(FieldTestCase):
    def test_validate(self):
        field = Str(
            title='Str field',
            description='',
            readonly=0,
            required=0)
        self.assertEquals(None, field.validate(None))
        self.assertEquals('foo', field.validate('foo'))
        self.assertEquals('', field.validate(''))
 
    def test_validate_required(self):
        field = Str(
            title='Str field required',
            description='',
            readonly=0,
            required=1)
        self.assertRaises(ValidationError, field.validate, None)
        self.assertEquals('foo', field.validate('foo'))
        self.assertRaises(ValidationError, field.validate, '')

class BoolTestCase(FieldTestCase):
    def test_validate(self):
        field = Bool(
            title='Bool field',
            description='',
            readonly=0,
            required=0)
        self.assertEquals(None, field.validate(None))
        self.assertEquals(1, field.validate(1))
        self.assertEquals(0, field.validate(0))
        self.assertEquals(1, field.validate(10))
        self.assertEquals(1, field.validate(-10))

    def test_validate(self):
        field = Bool(
            title='Bool field required',
            description='',
            readonly=0,
            required=1)
        self.assertRaises(ValidationError, field.validate, None)

class IntTestCase(FieldTestCase):
    def test_validate(self):
        field = Int(
            title='Int field',
            description='',
            readonly=0,
            required=0)
        self.assertEquals(None, field.validate(None))
        self.assertEquals(10, field.validate(10))
        self.assertEquals(0, field.validate(0))
        self.assertEquals(-1, field.validate(-1))
 
    def test_validate_required(self):
        field = Int(
            title='Int field required',
            description='',
            readonly=0,
            required=1)
        self.assertRaises(ValidationError, field.validate, None)
        self.assertEquals(10, field.validate(10))
        self.assertEquals(0, field.validate(0))
        self.assertEquals(-1, field.validate(-1))

    def test_validate_min(self):
        field = Int(
            title='Int field',
            description='',
            readonly=0,
            required=0,
            min=10)
        self.assertEquals(None, field.validate(None))
        self.assertEquals(10, field.validate(10))
        self.assertEquals(20, field.validate(20))
        self.assertRaises(ValidationError, field.validate, 9)
        self.assertRaises(ValidationError, field.validate, -10)

    def test_validate_max(self):
        field = Int(
            title='Int field',
            description='',
            readonly=0,
            required=0,
            max=10)
        self.assertEquals(None, field.validate(None))
        self.assertEquals(5, field.validate(5))
        self.assertEquals(9, field.validate(9))
        self.assertRaises(ValidationError, field.validate, 10)
        self.assertRaises(ValidationError, field.validate, 20)

    def test_validate_min_max(self):
        field = Int(
            title='Int field',
            description='',
            readonly=0,
            required=0,
            min=0,
            max=10)
        self.assertEquals(None, field.validate(None))
        self.assertEquals(0, field.validate(0))
        self.assertEquals(5, field.validate(5))
        self.assertEquals(9, field.validate(9))
        self.assertRaises(ValidationError, field.validate, -1)
        self.assertRaises(ValidationError, field.validate, 10)
        self.assertRaises(ValidationError, field.validate, 20)
        
def test_suite():
    return TestSuite((
        makeSuite(FieldTestCase),
        makeSuite(StrTestCase),
        makeSuite(BoolTestCase),
        makeSuite(IntTestCase),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
