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
$Id: testStrField.py,v 1.3 2002/09/11 22:06:41 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from Zope.Schema import Bytes, Text, ErrorNames
from Zope.Schema.Exceptions import ValidationError 
from testField import FieldTestBase

class StrTest(FieldTestBase):
    """Test the Str Field."""

    def testValidate(self):
        field = self._Str(title=u'Str field', description=u'',
                       readonly=0, required=0)
        field.validate(None)
        field.validate(self._convert('foo'))
        field.validate(self._convert(''))
    
    def testValidateRequired(self):

        # Note that if we want to require non-empty strings,
        # we need to set the min-length to 1.
        
        field = self._Str(title=u'Str field', description=u'',
                          readonly=0, required=1, min_length=1)
        field.validate(self._convert('foo'))

        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)
        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, self._convert(''))

    def testAllowedValues(self):
        field = self._Str(title=u'Str field', description=u'',
                          readonly=0, required=0,
                          allowed_values=(self._convert('foo'),
                                          self._convert('bar')))
        field.validate(None)
        field.validate(self._convert('foo'))

        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate, self._convert('blah'))

    def testValidateMinLength(self):
        field = self._Str(title=u'Str field', description=u'',
                       readonly=0, required=0, min_length=3)
        field.validate(None)
        field.validate(self._convert('333'))
        field.validate(self._convert('55555'))

        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, self._convert(''))
        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, self._convert('22'))
        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, self._convert('1'))

    def testValidateMaxLength(self):
        field = self._Str(title=u'Str field', description=u'',
                       readonly=0, required=0, max_length=5)
        field.validate(None)
        field.validate(self._convert(''))
        field.validate(self._convert('333'))
        field.validate(self._convert('55555'))

        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    self._convert('666666'))
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    self._convert('999999999'))

    def testValidateMinLengthAndMaxLength(self):
        field = self._Str(title=u'Str field', description=u'',
                       readonly=0, required=0, min_length=3, max_length=5)

        field.validate(None)
        field.validate(self._convert('333'))
        field.validate(self._convert('4444'))
        field.validate(self._convert('55555'))
        
        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, self._convert('22'))
        self.assertRaisesErrorNames(ErrorNames.TooShort,
                                    field.validate, self._convert('22'))
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    self._convert('666666'))
        self.assertRaisesErrorNames(ErrorNames.TooLong, field.validate,
                                    self._convert('999999999'))

class BytesTest(StrTest):
    _Str = Bytes
    _convert = str

    def testBadStringType(self):
        field = Bytes()
        self.assertRaises(ValidationError, field.validate, u'hello')
        

class TextTest(StrTest):
    _Str = Text
    def _convert(self, v):
        return unicode(v, 'ascii')

    def testBadStringType(self):
        field = Text()
        self.assertRaises(ValidationError, field.validate, 'hello')


def test_suite():
    return TestSuite((makeSuite(BytesTest), makeSuite(TextTest)))

if __name__ == '__main__':
    main(defaultTest='test_suite')
