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
$Id: testBoolField.py,v 1.1 2002/07/14 18:51:27 faassen Exp $
"""
from unittest import TestSuite, main, makeSuite
from Schema import Bool, ErrorNames, ValidationError
from testField import FieldTest
from Schema.Exceptions import ValidationError

class BoolTest(FieldTest):
    """Test the Bool Field."""

    def testValidate(self):
        field = Bool(id="field", title='Bool field', description='',
                        readonly=0, required=0)
        try:
            field.validate(None)
            field.validate(1)
            field.validate(0)
            field.validate(10)
            field.validate(-10)
        except ValidationError, e:
            self.unexpectedValidationError(e)

    def testValidateRequired(self):
        field = Bool(id="field", title='Bool field', description='',
                        readonly=0, required=1)
        try:
            field.validate(1)
            field.validate(0)
        except ValidationError, e:
            self.unexpectedValidationError(e)

        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testAllowedValues(self):
        field = Bool(id="field", title='Bool field', description='',
                        readonly=0, required=0, allowed_values=(0,))
        try:
            field.validate(None)
            field.validate(0)
        except ValidationError, e:
            self.unexpectedValidationError(e)
        
        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, 1)


def test_suite():
    return TestSuite((
        makeSuite(BoolTest),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
