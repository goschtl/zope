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
$Id: testIntegerField.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from unittest import TestSuite, main, makeSuite
from Schema import Integer, ErrorNames
from testField import FieldTest

class IntegerTest(FieldTest):
    """Test the Integer Field."""

    def testValidate(self):
        field = Integer(id="field", title='Integer field', description='',
                        readonly=0, required=0)
        self.assertEqual(None, field.validate(None))
        self.assertEqual(10, field.validate(10))
        self.assertEqual(0, field.validate(0))
        self.assertEqual(-1, field.validate(-1))

    def testValidateRequired(self):
        field = Integer(id="field", title='Integer field', description='',
                        readonly=0, required=1)
        self.assertEqual(10, field.validate(10))
        self.assertEqual(0, field.validate(0))
        self.assertEqual(-1, field.validate(-1))
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testAllowedValues(self):
        field = Integer(id="field", title='Integer field', description='',
                        readonly=0, required=0, allowed_values=(-1, 2))
        self.assertEqual(None, field.validate(None))
        self.assertEqual(2, field.validate(2))
        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, 4)

    def testValidateMin(self):
        field = Integer(id="field", title='Integer field', description='',
                        readonly=0, required=0, min=10)
        self.assertEqual(None, field.validate(None))
        self.assertEqual(10, field.validate(10))
        self.assertEqual(20, field.validate(20))
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, 9)
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -10)

    def testValidateMax(self):
        field = Integer(id="field", title='Integer field', description='',
                        readonly=0, required=0, max=10)
        self.assertEqual(None, field.validate(None))
        self.assertEqual(5, field.validate(5))
        self.assertEqual(9, field.validate(9))
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 11)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 20)

    def testValidateMinAndMax(self):
        field = Integer(id="field", title='Integer field', description='',
                        readonly=0, required=0, min=0, max=10)
        self.assertEqual(None, field.validate(None))
        self.assertEqual(0, field.validate(0))
        self.assertEqual(5, field.validate(5))
        self.assertEqual(10, field.validate(10))
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -10)
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, -1)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 11)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, 20)


def test_suite():
    return TestSuite((
        makeSuite(IntegerTest),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
