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
$Id: _field.py,v 1.7 2003/04/10 09:34:30 paul Exp $
"""
__metaclass__ = type

from zope.interface.implements import implements

from zope.schema.interfaces import ValidationError
from zope.schema.errornames import WrongContainedType

from zope.schema.interfaces import IField, IContainer, IIterable, IOrderable
from zope.schema.interfaces import IMinMaxLen, IValueSet, IText, ITextLine
from zope.schema.interfaces import ISourceText
from zope.schema.interfaces import IBool, IInt, IBytes, IBytesLine, IFloat
from zope.schema.interfaces import IDatetime, ISequence, ITuple, IList, IDict
from zope.schema.interfaces import IPassword

from zope.schema._bootstrapfields import Field, Container, Iterable, Orderable
from zope.schema._bootstrapfields import MinMaxLen, ValueSet
from zope.schema._bootstrapfields import Text, TextLine, Bool, Int, Password
from zope.schema.fieldproperty import FieldProperty
from datetime import datetime

# Fix up bootstrap field types
Field.title       = FieldProperty(IField['title'])
Field.description = FieldProperty(IField['description'])
Field.required    = FieldProperty(IField['required'])
Field.readonly    = FieldProperty(IField['readonly'])
# Default is already taken care of
implements(Field, IField)

implements(Container, IContainer)
implements(Iterable, IIterable)
implements(Orderable, IOrderable)

MinMaxLen.min_length = FieldProperty(IMinMaxLen['min_length'])
MinMaxLen.max_length = FieldProperty(IMinMaxLen['max_length'])
implements(MinMaxLen, IMinMaxLen)

implements(ValueSet, IValueSet)

implements(Text, IText)
implements(TextLine, ITextLine)
implements(Password, IPassword)
implements(Bool, IBool)
implements(Int, IInt)

class SourceText(Text):
    __doc__ = ISourceText.__doc__
    __implements__ = ISourceText
    _type = unicode

class Bytes(MinMaxLen, ValueSet):
    __doc__ = IBytes.__doc__
    __implements__ = IBytes

    _type = str

class BytesLine(Bytes):
    """A Text field with no newlines."""

    __implements__ = IBytesLine

    def constraint(self, value):
        # XXX we should probably use a more general definition of newlines
        return '\n' not in value


class Float(ValueSet, Orderable):
    __doc__ = IFloat.__doc__
    __implements__ = IFloat
    _type = float

class Datetime(ValueSet, Orderable):
    __doc__ = IDatetime.__doc__
    __implements__ = IDatetime
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
    __doc__ = ISequence.__doc__
    __implements__ = ISequence
    value_types = FieldProperty(ISequence['value_types'])

    def __init__(self, value_types=None, **kw):
        super(Sequence, self).__init__(**kw)
        self.value_types = value_types

    def _validate(self, value):
        super(Sequence, self)._validate(value)
        errors = _validate_sequence(self.value_types, value)
        if errors:
            raise ValidationError(WrongContainedType, errors)


class Tuple(Sequence):
    """A field representing a Tuple."""
    __implements__ = ITuple
    _type = tuple


class List(Sequence):
    """A field representing a List."""
    __implements__ = IList
    _type = list


class Dict(MinMaxLen, Iterable):
    """A field representing a Dict."""
    __implements__ = IDict
    _type = dict
    key_types   = FieldProperty(IDict['key_types'])
    value_types = FieldProperty(IDict['value_types'])

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
                raise ValidationError(WrongContainedType, errors)

        finally:
            errors = None
