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
$Id: test_floatfield.py,v 1.2 2002/12/25 14:15:21 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from zope.schema import Float
from zope.schema import errornames
from zope.schema.tests.test_field import FieldTestBase

class FloatTest(FieldTestBase):
    """Test the Float Field."""

    _Field_Factory = Float

    def testValidate(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=False, required=False)
        field.validate(None)
        field.validate(10.0)
        field.validate(0.93)
        field.validate(1000.0003)

    def testValidateRequired(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=False, required=True)
        field.validate(10.0)
        field.validate(0.93)
        field.validate(1000.0003)

        self.assertRaisesErrorNames(errornames.RequiredMissing,
                                    field.validate, None)
    def testAllowedValues(self):
        field = Float(title=u'Integer field', description=u'',
                      readonly=False, required=False,
                      allowed_values=(0.1, 2.6))
        field.validate(None)
        field.validate(2.6)

        self.assertRaisesErrorNames(errornames.InvalidValue,
                                    field.validate, -5.4)

    def testValidateMin(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=False, required=False, min=10.5)
        field.validate(None)
        field.validate(10.6)
        field.validate(20.2)

        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, -9.0)
        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, 10.4)

    def testValidateMax(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=False, required=False, max=10.5)
        field.validate(None)
        field.validate(5.3)
        field.validate(-9.1)

        self.assertRaisesErrorNames(errornames.TooBig, field.validate, 10.51)
        self.assertRaisesErrorNames(errornames.TooBig, field.validate, 20.7)

    def testValidateMinAndMax(self):
        field = Float(title=u'Float field', description=u'',
                        readonly=False, required=False, min=-0.6, max=10.1)
        field.validate(None)
        field.validate(0.0)
        field.validate(-0.03)
        field.validate(10.0001)

        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, -10.0)
        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, -1.6)
        self.assertRaisesErrorNames(errornames.TooBig, field.validate, 11.45)
        self.assertRaisesErrorNames(errornames.TooBig, field.validate, 20.02)


def test_suite():
    return makeSuite(FloatTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
