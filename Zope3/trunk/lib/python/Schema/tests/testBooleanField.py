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
$Id: testBooleanField.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from unittest import TestSuite, main, makeSuite
from Schema import Boolean, ErrorNames
from testField import FieldTest

class BooleanTest(FieldTest):
    """Test the Boolean Field."""

    def testValidate(self):
        field = Boolean(id="field", title='Boolean field', description='',
                        readonly=0, required=0)
        self.assertEqual(None, field.validate(None))
        self.assertEqual(1, field.validate(1))
        self.assertEqual(0, field.validate(0))
        self.assertEqual(10, field.validate(10))
        self.assertEqual(-10, field.validate(-10))

    def testValidateRequired(self):
        field = Boolean(id="field", title='Boolean field', description='',
                        readonly=0, required=1)
        self.assertEqual(1, field.validate(1))
        self.assertEqual(0, field.validate(0))
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testAllowedValues(self):
        field = Boolean(id="field", title='Boolean field', description='',
                        readonly=0, required=0, allowed_values=(0,))
        self.assertEqual(None, field.validate(None))
        self.assertEqual(0, field.validate(0))
        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, 1)


def test_suite():
    return TestSuite((
        makeSuite(BooleanTest),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
