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
This set of tests exercises both Tuple and Sequence.  The only
behavior Tuple adds to sequence is the restriction of the type
to 'tuple'.

$Id: test_tuplefield.py,v 1.3 2003/01/25 03:53:40 rdmurray Exp $
"""
from unittest import TestSuite, main, makeSuite
from zope.schema import Sequence, Tuple, Int, Float
from zope.schema import errornames
from zope.schema.tests.test_field import FieldTestBase

class SequenceTest(FieldTestBase):
    """Test the Sequence Field."""

    _Field_Factory = Sequence

    def testValidate(self):
        field = self._Field_Factory(title=u'test field', description=u'',
                                    readonly=False, required=False)
        field.validate(None)
        field.validate(())
        field.validate([])
        field.validate('')
        field.validate({})
        field.validate([1, 2])

        self.assertRaisesErrorNames(errornames.NotAContainer,
                                    field.validate, 1)

    def testValidateRequired(self):
        field = self._Field_Factory(title=u'test field', description=u'',
                                    readonly=False, required=True)
        field.validate([1, 2])

        self.assertRaisesErrorNames(errornames.RequiredMissing,
                                    field.validate, None)


class TupleTest(FieldTestBase):
    """Test the Tuple Field."""

    _Field_Factory = Tuple

    def testValidate(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False)
        field.validate(None)
        field.validate(())
        field.validate((1, 2))
        field.validate((3,))

        self.assertRaisesErrorNames(errornames.WrongType,
                                    field.validate, [1, 2, 3])
        self.assertRaisesErrorNames(errornames.WrongType,
                                    field.validate, 'abc')
        self.assertRaisesErrorNames(errornames.WrongType,
                                    field.validate, 1)
        self.assertRaisesErrorNames(errornames.WrongType,
                                    field.validate, {})

    def testValidateRequired(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=True)
        field.validate(())
        field.validate((1, 2))
        field.validate((3,))

        self.assertRaisesErrorNames(errornames.RequiredMissing,
                                    field.validate, None)

    def testValidateMinValues(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False, min_length=2)
        field.validate(None)
        field.validate((1, 2))
        field.validate((1, 2, 3))

        self.assertRaisesErrorNames(errornames.TooShort,
                                    field.validate, ())
        self.assertRaisesErrorNames(errornames.TooShort,
                                    field.validate, (1,))

    def testValidateMaxValues(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False, max_length=2)
        field.validate(None)
        field.validate(())
        field.validate((1, 2))

        self.assertRaisesErrorNames(errornames.TooLong,
                                    field.validate, (1, 2, 3, 4))
        self.assertRaisesErrorNames(errornames.TooLong,
                                    field.validate, (1, 2, 3))

    def testValidateMinValuesAndMaxValues(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False,
                      min_length=1, max_length=2)
        field.validate(None)
        field.validate((1, ))
        field.validate((1, 2))

        self.assertRaisesErrorNames(errornames.TooShort,
                                    field.validate, ())
        self.assertRaisesErrorNames(errornames.TooLong,
                                    field.validate, (1, 2, 3))

    def testValidateValueTypes(self):
        field = Tuple(title=u'Tuple field', description=u'',
                      readonly=False, required=False,
                      value_types=(Int(), Float()))
        field.validate(None)
        field.validate((5.3,))
        field.validate((2, 2.3))

        self.assertRaisesErrorNames(errornames.WrongContainedType,
                                    field.validate, ('',) )
        self.assertRaisesErrorNames(errornames.WrongContainedType,
                                    field.validate, (2, '') )

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TupleTest))
    suite.addTest(makeSuite(SequenceTest))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
