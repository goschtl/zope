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
$Id: test_intfield.py,v 1.2 2002/12/25 14:15:21 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from zope.schema import Int
from zope.schema import errornames
from zope.schema.tests.test_field import FieldTestBase

class IntTest(FieldTestBase):
    """Test the Int Field."""

    _Field_Factory = Int

    def testValidate(self):
        field = Int(title=u'Int field', description=u'',
                        readonly=False, required=False)
        field.validate(None)
        field.validate(10)
        field.validate(0)
        field.validate(-1)

    def testValidateRequired(self):
        field = Int(title=u'Int field', description=u'',
                    readonly=False, required=True)
        field.validate(10)
        field.validate(0)
        field.validate(-1)

        self.assertRaisesErrorNames(errornames.RequiredMissing,
                                    field.validate, None)

    def testAllowedValues(self):
        field = Int(title=u'Int field', description=u'',
                        readonly=False, required=False, allowed_values=(-1, 2))
        field.validate(None)
        field.validate(2)

        self.assertRaisesErrorNames(errornames.InvalidValue,
                                    field.validate, 4)

    def testValidateMin(self):
        field = Int(title=u'Int field', description=u'',
                        readonly=False, required=False, min=10)
        field.validate(None)
        field.validate(10)
        field.validate(20)

        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, 9)
        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, -10)

    def testValidateMax(self):
        field = Int(title=u'Int field', description=u'',
                        readonly=False, required=False, max=10)
        field.validate(None)
        field.validate(5)
        field.validate(9)

        self.assertRaisesErrorNames(errornames.TooBig, field.validate, 11)
        self.assertRaisesErrorNames(errornames.TooBig, field.validate, 20)

    def testValidateMinAndMax(self):
        field = Int(title=u'Int field', description=u'',
                        readonly=False, required=False, min=0, max=10)
        field.validate(None)
        field.validate(0)
        field.validate(5)
        field.validate(10)

        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, -10)
        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, -1)
        self.assertRaisesErrorNames(errornames.TooBig, field.validate, 11)
        self.assertRaisesErrorNames(errornames.TooBig, field.validate, 20)


def test_suite():
    return makeSuite(IntTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
