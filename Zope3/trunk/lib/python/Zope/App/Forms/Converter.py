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
$Id: Converter.py,v 1.2 2002/07/14 17:31:17 faassen Exp $
"""
from Zope.App.Forms.IConverter import IConverter
from Schema.IField import *

class Converter:
    """ """
    __implements__ =  IConverter

    def __init__(self, context):
        self.context = context

    def convert(self, value):
        'See Zope.App.Forms.IConverter.IConverter'
        return value


class FieldToFieldConverter(Converter):
    """ """
    __convert_from__ = IField
    __convert_to__ = IField

    def convert(self, value):
        'See Zope.App.Forms.IConverter.IConverter'
        assert isinstance(value, self.__convert_from__.type), 'Wrong Type'
        value = self.__convert_to__.type(value)
        assert isinstance(value, self.__convert_to__.type), 'Wrong Type'
        return value


class StrToIntConverter(FieldConverter):
    """ """
    __convert_from__ = IStr
    __convert_to__ = IInt


class StrToFloatConverter(FieldConverter):
    """ """
    __convert_from__ = IStr
    __convert_to__ = IFloat


class StrToBoolConverter(FieldConverter):
    """ """
    __convert_from__ = IStr
    __convert_to__ = IBool



class RequestConverter(Converter):
    """ """
    __convert_from__ = IRequest
    __convert_to__ = IStr
    
    field_prefix = 'field_'        

    def convert(self, value):
        'See Zope.App.Forms.IConverter.IConverter'
        request = self.context
        raw_value = request.form.get(self.field_prefix+value)
        return raw_value


class ContainerConverter(Converter):
    """ """
    converters = []

    def convert(self, value):
        'See Zope.App.Forms.IConverter.IConverter'
        for converter in converters:
            value = converter(self.context).convert(value)
        return value

    
