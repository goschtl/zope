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
$Id: Converter.py,v 1.4 2002/07/24 10:53:48 srichter Exp $
"""
from types import TupleType, ListType
ListTypes = (TupleType, ListType)
from Schema.IConverter import IConverter
from Schema.Converter import NullConverter
from Schema.IField import *


class RawToHomogeneousListConverter(NullConverter):
    """Converts a list of raw values to a list of values with a specific
    type."""

    def __init__(self, type):
        self.type = type

    def convert(self, value):
        result = []
        for elem in value:
            result.append(self.type(elem))
        return result
    

class FieldToFieldConverter(NullConverter):
    """ """
    __convert_from__ = IField
    __convert_to__ = IField

    def convert(self, value):
        'See Zope.App.Forms.IConverter.IConverter'
        assert isinstance(value, self.__convert_from__.type), 'Wrong Type'
        value = self.__convert_to__.type(value)
        assert isinstance(value, self.__convert_to__.type), 'Wrong Type'
        return value


class NoneToEmptyListConverter(NullConverter):
    """Converts None object to an empty list."""

    def convert(self, value):
        if value is None:
            return []
        else:
            return value


class ValueToSingleItemListConverter(NullConverter):
    """Converts a single value to a list with the value being the only
    element."""

    def convert(self, value):
        if not isinstance(value, ListTypes):
            return [value]
        else:
            return value


