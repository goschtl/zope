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
$Id: testFloatField.py,v 1.1 2002/09/05 18:55:04 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from Zope.Schema import Float, ErrorNames
from testField import FieldTest

class FloatTest(FieldTest):
    """Test the Float Field."""

    def testValidate(self):
        field = Float(id="field", title='Float field', description='',
                        readonly=0, required=0)
        field.validate(None)
        field.validate(10.0)
        field.validate(0.93)
        field.validate(1000.0003)
    
    def testValidateRequired(self):
        field = Float(id="field", title='Float field', description='',
                        readonly=0, required=1)
        field.validate(10.0)
        field.validate(0.93)
        field.validate(1000.0003)

        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)        
    def testAllowedValues(self):
        field = Float(id="field", title='Integer field', description='',
                        readonly=0, required=0, allowed_values=(0.1, 2.6))
        field.validate(None)
        field.validate(2.6)

        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, -5.4)

    def testValidateMin(self):
        field = Float(id="field", title='Float field', description='',
                        readonly=0, required=0, min=10.5)
        field.validate(None)
        field.validate(10.6)
        field.validate(20.2)

        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -9)
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, 10.4)

    def testValidateMax(self):
        field = Float(id="field", title='Float field', description='',
                        readonly=0, required=0, max=10.5)
        field.validate(None)
        field.validate(5.3)
        field.validate(-9.1)

        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 10.51)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 20.7)

    def testValidateMinAndMax(self):
        field = Float(id="field", title='Float field', description='',
                        readonly=0, required=0, min=-0.6, max=10.1)
        field.validate(None)
        field.validate(0)
        field.validate(-0.03)
        field.validate(10.0001)

        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -10)
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -1.6)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 11.45)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 20.02)

    def testValidateDecimals(self):
        field = Float(id="field", title='Float field', description='',
                        readonly=0, required=0, decimals=2)
        field.validate(None)
        field.validate(5.3)
        field.validate(-9.11)

        self.assertRaisesErrorNames(ErrorNames.TooManyDecimals,
                                    field.validate, 10.511)
        self.assertRaisesErrorNames(ErrorNames.TooManyDecimals,
                                    field.validate, 20.7122)


def test_suite():
    return makeSuite(FloatTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
