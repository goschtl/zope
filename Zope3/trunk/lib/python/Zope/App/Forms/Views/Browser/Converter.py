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
$Id: Converter.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from Zope.App.Forms.Converter import *
from Schema.IField import *


class RequestToFieldConverter(Converter):
    """Base class that defines how to convert from the Request to a Field.
    Note that the value argument for the convert method is a string
    containing the name of the variable in the Request."""
    __convert_from__ = IRequest
    __convert_to__ = IField
    
    field_prefix = 'field_'        

    def convert(self, value):
        'See Zope.App.Forms.IConverter.IConverter'
        request = self.context
        raw_value = request.form.get(self.field_prefix+value)
        return raw_value


class RequestToStringConverter(Converter):
    """A specific class converting the in the request contained variable to
    a string."""
    __convert_from__ = IRequest
    __convert_to__ = IString


class RequestToIntegerConverter(ContainerConverter):
    """Convert from Request to an Integer."""
    converters = [RequestToStringConverter, StringToIntegerConverter]


class RequestToFloatConverter(ContainerConverter):
    """Convert from Request to an Float."""
    converters = [RequestToStringConverter, StringToFloatConverter]
