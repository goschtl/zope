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
$Id: _Field.py,v 1.10 2002/07/19 13:12:30 srichter Exp $
"""
from Interface.Attribute import Attribute
from Interface.Implements import objectImplements

from Exceptions import StopValidation, ValidationError
import ErrorNames


class Field(Attribute):
    # we don't implement the same interface Attribute
    __implements__ = ()
    type = None
    default = None
    setter = None
    getter = None
    required = 0
    allowed_values = []
    
    def __init__(self, **kw):
        """Pass in field values as keyword parameters."""
        for key, value in kw.items():
            setattr(self, key, value)
        super(Field, self).__init__(self.title or 'no title')

    def validate(self, value):
        try:
            return self.validator(self).validate(value)
        except StopValidation:
            return value

class Str(Field):
    """A field representing a Str."""
    type = str, unicode
    min_length = None
    max_length = None

class Bool(Field):
    """A field representing a Bool."""
    # XXX Do we really expect this to be an int?
    # The BoolTest only work if Bool corresponds to Python's int.
    type = int

class Int(Field):
    """A field representing a Integer."""
    type = int
    min = max = None

class Float(Field):
    """A field representing a Floating Point."""
    type = float, int
    min = max = None
    decimals = None

class Tuple(Field):
    """A field representing a Tuple."""
    type = tuple
    value_types = None
    min_values = max_values = None

class List(Field):
    """A field representing a List."""
    type = list
    value_types = None
    min_values = max_values = None

class Dict(Field):
    """A field representing a Dict."""
    type = dict
    min_values = max_values = None
    key_types = value_types = None


