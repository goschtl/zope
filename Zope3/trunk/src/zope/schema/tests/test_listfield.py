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
$Id: test_listfield.py,v 1.2 2002/12/25 14:15:21 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from zope.schema import List, Int, Float
from zope.schema import errornames
from zope.schema.tests.test_field import FieldTestBase

class ListTest(FieldTestBase):
    """Test the List Field."""

    _Field_Factory = List

    def testValidate(self):
        field = List(title=u'List field', description=u'',
                     readonly=False, required=False)
        field.validate(None)
        field.validate([])
        field.validate([1, 2])
        field.validate([3,])

    def testValidateRequired(self):
        field = List(title=u'List field', description=u'',
                     readonly=False, required=True)
        field.validate([])
        field.validate([1, 2])
        field.validate([3,])

        self.assertRaisesErrorNames(errornames.RequiredMissing,
                                    field.validate, None)

    def testValidateMinValues(self):
        field = List(title=u'List field', description=u'',
                     readonly=False, required=False, min_length=2)
        field.validate(None)
        field.validate([1, 2])
        field.validate([1, 2, 3])

        self.assertRaisesErrorNames(errornames.TooShort,
                                    field.validate, [])
        self.assertRaisesErrorNames(errornames.TooShort,
                                    field.validate, [1,])

    def testValidateMaxValues(self):
        field = List(title=u'List field', description=u'',
                     readonly=False, required=False, max_length=2)
        field.validate(None)
        field.validate([])
        field.validate([1, 2])

        self.assertRaisesErrorNames(errornames.TooLong,
                                    field.validate, [1, 2, 3, 4])
        self.assertRaisesErrorNames(errornames.TooLong,
                                    field.validate, [1, 2, 3])

    def testValidateMinValuesAndMaxValues(self):
        field = List(title=u'List field', description=u'',
                     readonly=False, required=False,
                     min_length=1, max_length=2)
        field.validate(None)
        field.validate([1, ])
        field.validate([1, 2])

        self.assertRaisesErrorNames(errornames.TooShort,
                                    field.validate, [])
        self.assertRaisesErrorNames(errornames.TooLong,
                                    field.validate, [1, 2, 3])

    def testValidateValueTypes(self):
        field = List(title=u'List field', description=u'',
                     readonly=False, required=False,
                     value_types=(Int(), Float()))
        field.validate(None)
        field.validate([5.3,])
        field.validate([2, 2.3])

        self.assertRaisesErrorNames(errornames.WrongContainedType,
                                    field.validate, ['',] )
        self.assertRaisesErrorNames(errornames.WrongContainedType,
                                    field.validate, [2, ''] )

def test_suite():
    return makeSuite(ListTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
