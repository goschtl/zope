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
$Id: testFloatField.py,v 1.2 2002/09/11 22:06:41 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from Zope.Schema import Float, ErrorNames
from testField import FieldTestBase

class FloatTest(FieldTestBase):
    """Test the Float Field."""

    def testValidate(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=0, required=0)
        field.validate(None)
        field.validate(10.0)
        field.validate(0.93)
        field.validate(1000.0003)
    
    def testValidateRequired(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=0, required=1)
        field.validate(10.0)
        field.validate(0.93)
        field.validate(1000.0003)

        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)        
    def testAllowedValues(self):
        field = Float(title=u'Integer field', description=u'',
                        readonly=0, required=0, allowed_values=(0.1, 2.6))
        field.validate(None)
        field.validate(2.6)

        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, -5.4)

    def testValidateMin(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=0, required=0, min=10.5)
        field.validate(None)
        field.validate(10.6)
        field.validate(20.2)

        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -9.0)
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, 10.4)

    def testValidateMax(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=0, required=0, max=10.5)
        field.validate(None)
        field.validate(5.3)
        field.validate(-9.1)

        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 10.51)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 20.7)

    def testValidateMinAndMax(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=0, required=0, min=-0.6, max=10.1)
        field.validate(None)
        field.validate(0.0)
        field.validate(-0.03)
        field.validate(10.0001)

        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -10.0)
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -1.6)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 11.45)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 20.02)


def test_suite():
    return makeSuite(FloatTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
