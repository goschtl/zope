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
$Id: _Field.py,v 1.7 2002/12/05 13:27:06 dannu Exp $
"""
__metaclass__ = type

from Interface.Implements import implements

from Exceptions import ValidationError
import ErrorNames

import IField
from _bootstrapFields import Field, Container, Iterable, Orderable, MinMaxLen
from _bootstrapFields import ValueSet, Text, TextLine, Bool, Int
from FieldProperty import FieldProperty
from datetime import datetime

# Fix up bootstrap field types
Field.title       = FieldProperty(IField.IField['title'])
Field.description = FieldProperty(IField.IField['description'])
Field.required    = FieldProperty(IField.IField['required'])
Field.readonly    = FieldProperty(IField.IField['readonly'])
# Default is already taken care of
implements(Field, IField.IField)

implements(Container, IField.IContainer)
implements(Iterable, IField.IIterable)
implements(Orderable, IField.IOrderable)

MinMaxLen.min_length = FieldProperty(IField.IMinMaxLen['min_length'])
MinMaxLen.max_length = FieldProperty(IField.IMinMaxLen['max_length'])
implements(MinMaxLen, IField.IMinMaxLen)

implements(ValueSet, IField.IValueSet)

implements(Text, IField.IText)
implements(TextLine, IField.ITextLine)
implements(Bool, IField.IBool)
implements(Int, IField.IInt)
            
class Bytes(MinMaxLen, ValueSet):
    __doc__ = IField.IBytes.__doc__
    __implements__ = IField.IBytes
    
    _type = str

class Line(Bytes):
    """A Text field with no newlines."""

    __implements__ = IField.IBytesLine

    def constraint(self, value):
        # XXX we should probably use a more general definition of newlines
        return '\n' not in value
    

class Float(ValueSet, Orderable):
    __doc__ = IField.IFloat.__doc__
    __implements__ = IField.IFloat
    _type = float

class Datetime(ValueSet, Orderable):
    __doc__ = IField.IDatetime.__doc__
    __implements__ = IField.IDatetime
    _type = datetime

def _validate_sequence(value_types, value, errors=None):
    if errors is None:
        errors = []
        
    if value_types is None:
        return errors

    for item in value:
        error = None
        for t in value_types:
            try:
                t.validate(item)
            except ValidationError, error:
                pass
            else:
                # We validated, so clear error (if any) and done with
                # this value
                error = None
                break

        if error is not None:
            errors.append(error)

    return errors
    

class Sequence(MinMaxLen, Iterable):
    __doc__ = IField.ISequence.__doc__
    value_types = FieldProperty(IField.ISequence['value_types'])

    def __init__(self, value_types=None, **kw):
        super(Sequence, self).__init__(**kw)
        self.value_types = value_types

    def _validate(self, value):
        super(Sequence, self)._validate(value)
        try:
            errors = _validate_sequence(self.value_types, value)
            if errors:
                raise ValidationError(ErrorNames.WrongContainedType, errors)
                
        finally:
            errors = None

class Tuple(Sequence):
    """A field representing a Tuple."""
    __implements__ = IField.ITuple
    _type = tuple

class List(Sequence):
    """A field representing a List."""
    __implements__ = IField.IList
    _type = list

class Dict(MinMaxLen, Iterable):
    """A field representing a Dict."""
    __implements__ = IField.IDict
    _type = dict
    key_types   = FieldProperty(IField.IDict['key_types'])
    value_types = FieldProperty(IField.IDict['value_types'])

    def __init__(self, key_types=None, value_types=None, **kw):
        super(Dict, self).__init__(**kw)
        self.key_types = key_types
        self.value_types = value_types

    def _validate(self, value):
        super(Dict, self)._validate(value)
        errors = []
        try:
            if self.value_types:
                errors = _validate_sequence(self.value_types, value.values(),
                                            errors)
            errors = _validate_sequence(self.key_types, value, errors)

            if errors:
                raise ValidationError(ErrorNames.WrongContainedType, errors)
                
        finally:
            errors = None

