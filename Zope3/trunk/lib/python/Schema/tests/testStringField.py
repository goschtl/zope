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
$Id: testStringField.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from unittest import TestSuite, main, makeSuite
from Schema import String, ErrorNames
from testField import FieldTest

class StringTest(FieldTest):
    """Test the String Field."""

    def testValidate(self):
        field = String(id='field', title='String field', description='',
                       readonly=0, required=0)
        self.assertEqual(None, field.validate(None))
        self.assertEqual('foo', field.validate('foo'))
        self.assertEqual('', field.validate(''))
        
    def testValidateRequired(self):
        field = String(id='field', title='String field', description='',
                       readonly=0, required=1)
        self.assertEqual('foo', field.validate('foo'))
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)
        self.assertRaisesErrorNames(ErrorNames.RequiredEmptyString,
                                    field.validate, '')

    def testAllowedValues(self):
        field = String(id="field", title='String field', description='',
                        readonly=0, required=0, allowed_values=('foo', 'bar'))
        self.assertEqual(None, field.validate(None))
        self.assertEqual('foo', field.validate('foo'))
        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, 'blah')

    def testValidateMinLength(self):
        field = String(id='field', title='String field', description='',
                       readonly=0, required=0, min_length=3)
        self.assertEqual(None, field.validate(None))
        self.assertEqual('333', field.validate('333'))
        self.assertEqual('55555', field.validate('55555'))
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '1')

    def testValidateMaxLength(self):
        field = String(id='field', title='String field', description='',
                       readonly=0, required=0, max_length=5)
        self.assertEqual(None, field.validate(None))
        self.assertEqual('', field.validate(''))
        self.assertEqual('333', field.validate('333'))
        self.assertEqual('55555', field.validate('55555'))
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    '666666')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    '999999999')

    def testValidateMinLengthAndMaxLength(self):
        field = String(id='field', title='String field', description='',
                       readonly=0, required=0, min_length=3, max_length=5)
        self.assertEqual(None, field.validate(None))
        self.assertEqual('333', field.validate('333'))
        self.assertEqual('4444', field.validate('4444'))
        self.assertEqual('55555', field.validate('55555'))
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooShort, field.validate, '22')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    '666666')
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    '999999999')

    def testValidateWhiteSpace(self):
        field = String(id='field', title='String field', description='',
                       readonly=0, required=0, whitespaces="preserve")
        self.assertEqual(None, field.validate(None))
        self.assertEqual('sample', field.validate('sample'))
        self.assertEqual('  sample  ', field.validate('  sample  '))
        self.assertEqual('  sam\tple  ', field.validate('  sam\tple  '))

        field = String(id='field', title='String field', description='',
                       readonly=0, required=0, whitespaces="replace")
        self.assertEqual(None, field.validate(None))
        self.assertEqual('sample', field.validate('sample'))
        self.assertEqual('  sample  ', field.validate('  sample  '))
        self.assertEqual('  sam ple  ', field.validate('  sam\tple  '))
        self.assertEqual('  sam ple  ', field.validate('  sam\rple  '))
        self.assertEqual('  sam ple  ', field.validate('  sam\nple  '))

        field = String(id='field', title='String field', description='',
                       readonly=0, required=0, whitespaces="collapse")
        self.assertEqual(None, field.validate(None))
        self.assertEqual('sample', field.validate('sample'))
        self.assertEqual('sample', field.validate('  sample  '))
        self.assertEqual('sam ple', field.validate('  sam\tple  '))

        field = String(id='field', title='String field', description='',
                       readonly=0, required=0, whitespaces="strip")
        self.assertEqual(None, field.validate(None))
        self.assertEqual('sample', field.validate('sample'))
        self.assertEqual('sample', field.validate('  sample  '))
        self.assertEqual('sam\tple', field.validate('  sam\tple  '))


def test_suite():
    return TestSuite((
        makeSuite(StringTest),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
