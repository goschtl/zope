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
$Id: testTupleField.py,v 1.1 2002/09/05 18:55:04 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from Zope.Schema import Tuple, Int, Float, ErrorNames
from testField import FieldTest

class TupleTest(FieldTest):
    """Test the Tuple Field."""

    def testValidate(self):
        field = Tuple(id="field", title='Tuple field', description='',
                        readonly=0, required=0)
        field.validate(None)
        field.validate(())
        field.validate((1, 2))
        field.validate((3,))
        
    def testValidateRequired(self):
        field = Tuple(id="field", title='Tuple field', description='',
                        readonly=0, required=1)
        field.validate(())
        field.validate((1, 2))
        field.validate((3,))

        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testValidateMinValues(self):
        field = Tuple(id="field", title='Tuple field', description='',
                        readonly=0, required=0, min_values=2)
        field.validate(None)
        field.validate((1, 2))
        field.validate((1, 2, 3))

        self.assertRaisesErrorNames(ErrorNames.NotEnoughElements,
                                    field.validate, ())
        self.assertRaisesErrorNames(ErrorNames.NotEnoughElements,
                                    field.validate, (1,))

    def testValidateMaxValues(self):
        field = Tuple(id="field", title='Tuple field', description='',
                        readonly=0, required=0, max_values=2)
        field.validate(None)
        field.validate(())
        field.validate((1, 2))

        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, (1, 2, 3, 4))
        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, (1, 2, 3))

    def testValidateMinValuesAndMaxValues(self):
        field = Tuple(id="field", title='Tuple field', description='',
                        readonly=0, required=0, min_values=1, max_values=2)
        field.validate(None)
        field.validate((1, ))
        field.validate((1, 2))

        self.assertRaisesErrorNames(ErrorNames.NotEnoughElements,
                                    field.validate, ())
        self.assertRaisesErrorNames(ErrorNames.TooManyElements,
                                    field.validate, (1, 2, 3))

    def testValidateValueTypes(self):
        field = Tuple(id="field", title='Tuple field', description='',
                        readonly=0, required=0, value_types=(Int, Float))
        field.validate(None)
        field.validate((5.3,))
        field.validate((2, 2.3))

        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, ('',) )
        self.assertRaisesErrorNames(ErrorNames.WrongContainedType,
                                    field.validate, (2, '') )

def test_suite():
    return makeSuite(TupleTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
