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
$Id: testStrField.py,v 1.1 2002/07/14 18:51:27 faassen Exp $
"""
from unittest import TestSuite, main, makeSuite
from Schema import Str, ErrorNames
from testField import FieldTest

class StrTest(FieldTest):
    """Test the Str Field."""

    def testValidate(self):
        field = Str(id='field', title='Str field', description='',
                       readonly=0, required=0)
        try:
            field.validate(None)
            field.validate('foo')
            field.validate('')
        except ValidationError, e:
            self.unexpectedValidationError(e)
        
    def testValidateRequired(self):
        field = Str(id='field', title='Str field', description='',
                       readonly=0, required=1)
        try:
            field.validate('foo')
        except ValidationError, e:
            self.unexpectedValidationError(e)
        
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)
        self.assertRaisesErrorNames(ErrorNames.RequiredEmptyStr,
                                    field.validate, '')

    def testAllowedValues(self):
        field = Str(id="field", title='Str field', description='',
                        readonly=0, required=0, allowed_values=('foo', 'bar'))
        try:
            field.validate(None)
            field.validate('foo')
        except ValidationError, e:
            self.unexpectedValidationError(e)
            
        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, 'blah')

    def testValidateMinLength(self):
        field = Str(id='field', title='Str field', description='',
                       readonly=0, required=0, min_length=3)
        try:
            field.validate(None)
            field.validate('333')
            field.validate('55555')
        except ValidationError, e:
            self.unexpectedValidationError(e)
            
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '1')

    def testValidateMaxLength(self):
        field = Str(id='field', title='Str field', description='',
                       readonly=0, required=0, max_length=5)
        try:
            field.validate(None)
            field.validate('')
            field.validate('333')
            field.validate('55555')
        except ValidationError, e:
            self.unexpectedValidationError(e)
        
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    '666666')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    '999999999')

    def testValidateMinLengthAndMaxLength(self):
        field = Str(id='field', title='Str field', description='',
                       readonly=0, required=0, min_length=3, max_length=5)

        try:
            field.validate(None)
            field.validate('333')
            field.validate('4444')
            field.validate('55555')
        except ValidationError, e:
            self.unexpectedValidationError(e)
            
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    '666666')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    '999999999')


def test_suite():
    return TestSuite((
        makeSuite(StrTest),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
