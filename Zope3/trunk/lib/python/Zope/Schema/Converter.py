##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
$Id: Converter.py,v 1.1 2002/09/05 18:55:03 jim Exp $
"""
from IConverter import IConverter
from Exceptions import ConversionError

# XXX is it worth is doing isImplementedBy checks in converters (input values)?
# if evil code could corrupt matters yes, but can it? (after all
# it'll also have to pass validation, unless the converter framework
# is used independently..something to ponder)

class NullConverter(object):
    """A converter that really doesn't do a thing.
    """
    __implements__ = IConverter

    def convert(self, value):
        return value

class CombinedConverter(object):
    """A converter that chains several converters to each other.
    """
    __implements__ = IConverter

    def __init__(self, converters):
        self._converters = converters
    
    def convert(self, value):
        for converter in self._converters:
            value = converter.convert(value)
        return value

class FunctionConverter(object):
    """Use a Python function to convert.
    Turns *any* Python exception into a conversion error.
    XXX Is this good/useful?
    """
    __implements__ = IConverter    

    def convert(self, value):
        try:
            return self._function(value)
        except Exception, e:
            raise ConversionError('Conversion error', e)
        
def _functionConverterFactory(klass_name, function):
    """Create a derived class of FunctionConvert which uses function.
    """
    klass = type(klass_name, (FunctionConverter,), {})
    klass._function = function
    return klass

StrToIntConverter= _functionConverterFactory('StrToIntConverter', int)
IntToStrConverter = _functionConverterFactory('IntToStrConverter', str)

StrToFloatConverter = _functionConverterFactory('StrToFloatConverter', float)
FloatToStrConverter = _functionConverterFactory('FloatToStrConverter', str)


class FileToStrConverter(object):
    __implements__ = IConverter    

    def convert(self, value):
        try:
            value = value.read()
        except Exception, e:
            raise ConversionError('Value is not a file object', e)
        else:
            if len(value):
                return value
            else:
                return None
