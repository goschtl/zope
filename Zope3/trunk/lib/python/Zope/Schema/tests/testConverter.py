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
"""Test conversion functionality of schema.

$Id: testConverter.py,v 1.1 2002/09/05 18:55:04 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Schema.Exceptions import ConversionError
from Zope.Schema.Converter import NullConverter, StrToIntConverter,\
     IntToStrConverter, CombinedConverter, StrToFloatConverter,\
     FloatToStrConverter

class ConverterTest(TestCase):
    def test_NullConverter(self):
        null_converter = NullConverter()
        self.assertEquals(1, null_converter.convert(1))
        self.assertEquals('foo', null_converter.convert('foo'))

    def test_StrToIntConverter(self):
        str_to_int_converter = StrToIntConverter()
        self.assertEquals(1, str_to_int_converter.convert('1'))
        self.assertEquals(100, str_to_int_converter.convert('100'))
        self.assertRaises(ConversionError, str_to_int_converter.convert, 'foo')

    def test_IntToStrConverter(self):
        int_to_str_converter = IntToStrConverter()
        self.assertEquals('1', int_to_str_converter.convert(1))

    def test_StrToFloatConverter(self):
        str_to_float_converter = StrToFloatConverter()
        self.assertEquals(1., str_to_float_converter.convert('1.0'))
        self.assertEquals(1., str_to_float_converter.convert('1'))
        self.assertRaises(ConversionError, str_to_float_converter.convert,
                          'foo')

    def test_FloatToStrConverter(self):
        float_to_str_converter = FloatToStrConverter()
        self.assertEquals('1.0', float_to_str_converter.convert(1.0))
        
    def test_CombinedConverter(self):
        combined_converter = CombinedConverter([StrToIntConverter(),
                                                IntToStrConverter()])
        self.assertEquals('1', combined_converter.convert('1'))
        self.assertRaises(ConversionError, combined_converter.convert, 'foo')
        
def test_suite():
    return makeSuite(ConverterTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
