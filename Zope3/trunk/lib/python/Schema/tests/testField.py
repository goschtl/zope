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

$Id: testField.py,v 1.3 2002/06/25 15:14:17 klawlf Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Schema.Exceptions import StopValidation, ValidationError

from Schema import Field, Int, Str, Bool
from Schema import IField
from Schema import ErrorNames

class FieldTestCase(TestCase):
    def assertRaisesErrorNames(self, error_name, f, *args, **kw):
        try:
            f(*args, **kw)
        except ValidationError, e:
            self.assertEquals(error_name, e.error_name)
            return
        self.fail('Expected ValidationError')

    def test_validate(self):
        field = Field(
            title='Not required field',
            description='',
            readonly=0,
            required=0)
        try:
            field.validate(None)
            field.validate('foo')
            field.validate(1)
            field.validate(0)
            field.validate('')
        except ValidationError, e:
            self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

    def test_validate_required(self):
        field = Field(
            title='Required field',
            description='',
            readonly=0,
            required=1)
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing, field.validate, None)
        try:
            field.validate('foo')
            field.validate(1)
            field.validate(0)
            field.validate('')
        except ValidationError, e:
            self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

class StrTestCase(FieldTestCase):
    def test_validate(self):
        field = Str(
            title='Str field',
            description='',
            readonly=0,
            required=0)
        try:
            field.validate(None)
            field.validate('foo')
            field.validate('')
        except ValidationError, e:
            self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

    def test_validate_required(self):
        field = Str(
            title='Str field required',
            description='',
            readonly=0,
            required=1)
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing, field.validate, None)
        try:
            field.validate('foo')
        except ValidationError, e:
            self.fail('Expected no ValidationError, but we got %s.' % e.error_name)
        self.assertRaises(ValidationError, field.validate, '')

    def test_validate_min(self):
        field = Str(
            title='Str field',
            description='',
            readonly=0,
            required=0,
            min_length=3)
        try:
           field.validate(None)
           field.validate('333')
           field.validate('55555')
        except ValidationError, e:
           self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '1')

    def test_validate_max(self):
        field = Str(
            title='Str field',
            description='',
            readonly=0,
            required=0,
            max_length=5)
        try:
           field.validate(None)
           field.validate('')
           field.validate('333')
           field.validate('55555')
        except ValidationError, e:
           self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate, '666666')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate, '999999999')

    def test_validate_min_max(self):
        field = Str(
            title='Str field',
            description='',
            readonly=0,
            required=0,
            min_length=3,
            max_length=5)
        try:
            field.validate(None)
            field.validate('333')
            field.validate('4444')
            field.validate('55555')
        except ValidationError, e:
           self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate, '666666')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate, '999999999')


class BoolTestCase(FieldTestCase):
    def test_validate(self):
        field = Bool(
            title='Bool field',
            description='',
            readonly=0,
            required=0)
        try:
            field.validate(None)
            field.validate(1)
            field.validate(0)
            field.validate(10)
            field.validate(-10)
        except ValidationError, e:
            self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

    def test_validate(self):
        field = Bool(
            title='Bool field required',
            description='',
            readonly=0,
            required=1)
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing, field.validate, None)

class IntTestCase(FieldTestCase):
    def test_validate(self):
        field = Int(
            title='Int field',
            description='',
            readonly=0,
            required=0)
        try:
            field.validate(None)
            field.validate(10)
            field.validate(0)
            field.validate(-1)
        except ValidationError, e:
           self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

    def test_validate_required(self):
        field = Int(
            title='Int field required',
            description='',
            readonly=0,
            required=1)
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing, field.validate, None)

        try:
            field.validate(10)
            field.validate(0)
            field.validate(-1)
        except ValidationError, e:
           self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

    def test_validate_min(self):
        field = Int(
            title='Int field',
            description='',
            readonly=0,
            required=0,
            min=10)
        try:
           field.validate(None)
           field.validate(10)
           field.validate(20)
        except ValidationError, e:
           self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, 9)
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -10)

    def test_validate_max(self):
        field = Int(
            title='Int field',
            description='',
            readonly=0,
            required=0,
            max=10)
        try:
           field.validate(None)
           field.validate(5)
           field.validate(9)
        except ValidationError, e:
           self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 11)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 20)

    def test_validate_min_max(self):
        field = Int(
            title='Int field',
            description='',
            readonly=0,
            required=0,
            min=0,
            max=10)
        try:
            field.validate(None)
            field.validate(0)
            field.validate(5)
            field.validate(10)
        except ValidationError, e:
           self.fail('Expected no ValidationError, but we got %s.' % e.error_name)

        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -10)
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -1)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 11)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 20)

def test_suite():
    return TestSuite((
        makeSuite(FieldTestCase),
        makeSuite(StrTestCase),
        makeSuite(BoolTestCase),
        makeSuite(IntTestCase),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
