# -*- coding: ISO-8859-1 -*-
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
"""Schema Fields

$Id: _field.py,v 1.31 2004/03/15 18:12:40 jim Exp $
"""
__metaclass__ = type

import warnings
import re

from zope.interface import classImplements, implements
from zope.interface.interfaces import IInterface
from zope.interface.interfaces import IMethod

from zope.schema.interfaces import ValidationError
from zope.schema.errornames import WrongContainedType, WrongType
from zope.schema import errornames

from zope.schema.interfaces import IField
from zope.schema.interfaces import IMinMaxLen, IText, ITextLine
from zope.schema.interfaces import ISourceText
from zope.schema.interfaces import IInterfaceField
from zope.schema.interfaces import IBytes, IASCII, IBytesLine
from zope.schema.interfaces import IBool, IInt, IFloat
from zope.schema.interfaces import IDatetime, ISequence, ITuple, IList, IDict
from zope.schema.interfaces import IPassword, IObject, IDate, IEnumeratedDate
from zope.schema.interfaces import IEnumeratedDatetime, IEnumeratedTextLine
from zope.schema.interfaces import IEnumeratedInt, IEnumeratedFloat
from zope.schema.interfaces import IURI, IId, IFromUnicode

from zope.schema._bootstrapfields import Field, Container, Iterable, Orderable
from zope.schema._bootstrapfields import MinMaxLen, Enumerated
from zope.schema._bootstrapfields import Text, TextLine, Bool, Int, Password
from zope.schema._bootstrapfields import EnumeratedTextLine, EnumeratedInt
from zope.schema.fieldproperty import FieldProperty
from datetime import datetime, date

# Fix up bootstrap field types
Field.title       = FieldProperty(IField['title'])
Field.description = FieldProperty(IField['description'])
Field.required    = FieldProperty(IField['required'])
Field.readonly    = FieldProperty(IField['readonly'])
# Default is already taken care of
classImplements(Field, IField)

MinMaxLen.min_length = FieldProperty(IMinMaxLen['min_length'])
MinMaxLen.max_length = FieldProperty(IMinMaxLen['max_length'])

classImplements(Text, IText)
classImplements(TextLine, ITextLine)
classImplements(Password, IPassword)
classImplements(Bool, IBool)
classImplements(Int, IInt)
classImplements(EnumeratedInt, IEnumeratedInt)
classImplements(EnumeratedTextLine, IEnumeratedTextLine)

class SourceText(Text):
    __doc__ = ISourceText.__doc__
    implements(ISourceText)
    _type = unicode

class Bytes(MinMaxLen, Field):
    __doc__ = IBytes.__doc__
    implements(IBytes, IFromUnicode)

    _type = str

    def fromUnicode(self, u):
        """
        >>> b = Bytes(constraint=lambda v: 'x' in v)

        >>> b.fromUnicode(u" foo x.y.z bat")
        ' foo x.y.z bat'
        >>> b.fromUnicode(u" foo y.z bat")
        Traceback (most recent call last):
        ...
        ValidationError: (u'Constraint not satisfied', ' foo y.z bat')

        """
        v = str(u)
        self.validate(v)
        return v

class ASCII(Bytes):
    __doc__ = IASCII.__doc__
    implements(IASCII)

    def _validate(self, value):
        """
        >>> ascii = ASCII()

        Make sure we accept empty strings:

        >>> empty = ''
        >>> ascii._validate(empty)

        and all kinds of alphanumeric strings:

        >>> alphanumeric = "Bob\'s my 23rd uncle"
        >>> ascii._validate(alphanumeric)

        >>> umlauts = "Köhlerstraße"
        >>> ascii._validate(umlauts)
        Traceback (most recent call last):
        ...
        ValidationError: Invalid value
        """
        super(ASCII, self)._validate(value)
        if not value:
            return
        if not max(map(ord, value)) < 128:
            raise ValidationError(errornames.InvalidValue)

class BytesLine(Bytes):
    """A Text field with no newlines."""

    implements(IBytesLine)

    def constraint(self, value):
        # XXX we should probably use a more general definition of newlines
        return '\n' not in value


class Float(Orderable, Field):
    __doc__ = IFloat.__doc__
    implements(IFloat, IFromUnicode)
    _type = float

    def __init__(self, *args, **kw):
        super(Float, self).__init__(*args, **kw)

    def fromUnicode(self, u):
        """
        >>> f = Float()
        >>> f.fromUnicode("1.25")
        1.25
        >>> f.fromUnicode("1.25.6")
        Traceback (most recent call last):
        ...
        ValueError: invalid literal for float(): 1.25.6
        """
        v = float(u)
        self.validate(v)
        return v

class EnumeratedFloat(Enumerated, Float):
    __doc__ = IEnumeratedFloat.__doc__
    implements(IEnumeratedFloat)

class Datetime(Orderable, Field):
    __doc__ = IDatetime.__doc__
    implements(IDatetime)
    _type = datetime

    def __init__(self, *args, **kw):
        super(Datetime, self).__init__(*args, **kw)

class EnumeratedDatetime(Enumerated, Datetime):
    __doc__ = IEnumeratedDatetime.__doc__
    implements(IEnumeratedDatetime)

class Date(Orderable, Field):
    __doc__ = IDate.__doc__
    implements(IDate)
    _type = date

class EnumeratedDate(Enumerated, Date):
    __doc__ = IEnumeratedDate.__doc__
    implements(IEnumeratedDate)

class InterfaceField(Field):
    __doc__ = IInterfaceField.__doc__
    implements(IInterfaceField)

    def _validate(self, value):
        super(InterfaceField, self)._validate(value)
        if not IInterface.providedBy(value):
            raise ValidationError(WrongType)

def _validate_sequence(value_type, value, errors=None):
    if errors is None:
        errors = []

    if value_type is None:
        return errors

    for item in value:
        error = None
        try:
            value_type.validate(item)
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


class Sequence(MinMaxLen, Iterable, Field):
    __doc__ = ISequence.__doc__
    implements(ISequence)
    value_type = None

    def __init__(self, value_type=None, **kw):
        super(Sequence, self).__init__(**kw)
        # whine if value_type is not a field
        if value_type is not None and not IField.providedBy(value_type):
            raise ValueError, "'value_type' must be field instance."
        self.value_type = value_type

    def _validate(self, value):
        super(Sequence, self)._validate(value)
        errors = _validate_sequence(self.value_type, value)
        if errors:
            raise ValidationError(WrongContainedType, errors)

class Tuple(Sequence):
    """A field representing a Tuple."""
    implements(ITuple)
    _type = tuple


class List(Sequence):
    """A field representing a List."""
    implements(IList)
    _type = list


def _validate_fields(schema, value, errors=None):
    if errors is None:
        errors = []  
    for name in schema.names(all=True):
        if not IMethod.providedBy(schema[name]):
            try:
                attribute = schema[name]
                if IField.providedBy(attribute):
                    # validate attributes that are fields  
                    attribute.validate(getattr(value, name))
            except ValidationError, error:
                errors.append(error)
            except AttributeError, error:
                # property for the given name is not implemented
                errors.append(errornames.SchemaNotFullyImplemented)
                
    return errors


class Object(Field):
    __doc__ = IObject.__doc__
    implements(IObject)

    def __init__(self, schema, **kw):
        if not IInterface.providedBy(schema):
            raise ValidationError(WrongType)
            
        self.schema = schema
        super(Object, self).__init__(**kw)
        
    def _validate(self, value):
        super(Object, self)._validate(value)
        
        # schema has to be implemented by value    
        if not self.schema.providedBy(value):
            raise ValidationError(errornames.SchemaNotProvided)
            
        # check the value against  schema
        errors = _validate_fields(self.schema, value)
        if errors:
            raise ValidationError(WrongContainedType, errors)


class Dict(MinMaxLen, Iterable, Field):
    """A field representing a Dict."""
    implements(IDict)
    _type = dict
    key_type   = None
    value_type = None

    def __init__(self, key_type=None, value_type=None, **kw):
        super(Dict, self).__init__(**kw)
        # whine if key_type or value_type is not a field
        if key_type is not None and not IField.providedBy(key_type):
            raise ValueError, "'key_type' must be field instance."
        if value_type is not None and not IField.providedBy(value_type):
            raise ValueError, "'value_type' must be field instance."
        self.key_type = key_type
        self.value_type = value_type

    def _validate(self, value):
        super(Dict, self)._validate(value)
        errors = []
        try:
            if self.value_type:
                errors = _validate_sequence(self.value_type, value.values(),
                                            errors)
            errors = _validate_sequence(self.key_type, value, errors)

            if errors:
                raise ValidationError(WrongContainedType, errors)

        finally:
            errors = None


_isuri = re.compile(
    r"[a-zA-z0-9+.-]+:"   # scheme
    r"\S*$"               # non space (should be pickier)
    ).match
class URI(BytesLine):
    """URI schema field
    """

    implements(IURI, IFromUnicode)

    def _validate(self, value):
        """
        >>> uri = URI(__name__='test')
        >>> uri.validate("http://www.python.org/foo/bar")
        >>> uri.validate("DAV:")
        >>> uri.validate("www.python.org/foo/bar")
        Traceback (most recent call last):
        ...
        ValidationError: ('Invalid uri', 'www.python.org/foo/bar')
        """

        super(URI, self)._validate(value)
        if _isuri(value):
            return

        raise ValidationError("Invalid uri", value)

    def fromUnicode(self, value):
        """
        >>> uri = URI(__name__='test')
        >>> uri.fromUnicode("http://www.python.org/foo/bar")
        'http://www.python.org/foo/bar'
        >>> uri.fromUnicode("          http://www.python.org/foo/bar")
        'http://www.python.org/foo/bar'
        >>> uri.fromUnicode("      \\n    http://www.python.org/foo/bar\\n")
        'http://www.python.org/foo/bar'
        >>> uri.fromUnicode("http://www.python.org/ foo/bar")
        Traceback (most recent call last):
        ...
        ValidationError: ('Invalid uri', 'http://www.python.org/ foo/bar')
        """
        v = str(value.strip())
        self.validate(v)
        return v


_isdotted = re.compile(
    r"([a-zA-Z][a-zA-z0-9_]*)"
    r"([.][a-zA-Z][a-zA-z0-9_]*)*"
    r"$" # use the whole line
    ).match

class Id(BytesLine):
    """Id field

    Values of id fields must be either uris or dotted names.
    """

    implements(IId, IFromUnicode)

    def _validate(self, value):
        """
        >>> id = Id(__name__='test')
        >>> id.validate("http://www.python.org/foo/bar")
        >>> id.validate("zope.app.content")
        >>> id.validate("zope.app.content/a")
        Traceback (most recent call last):
        ...
        ValidationError: ('Invalid id', 'zope.app.content/a')
        >>> id.validate("http://zope.app.content x y")
        Traceback (most recent call last):
        ...
        ValidationError: ('Invalid id', 'http://zope.app.content x y')
        """
        super(Id, self)._validate(value)
        if _isuri(value):
            return
        if _isdotted(value) and "." in value:
            return

        raise ValidationError("Invalid id", value)

    def fromUnicode(self, value):
        """
        >>> id = Id(__name__='test')
        >>> id.fromUnicode("http://www.python.org/foo/bar")
        'http://www.python.org/foo/bar'
        >>> id.fromUnicode(u" http://www.python.org/foo/bar ")
        'http://www.python.org/foo/bar'
        >>> id.fromUnicode("http://www.python.org/ foo/bar")
        Traceback (most recent call last):
        ...
        ValidationError: ('Invalid id', 'http://www.python.org/ foo/bar')
        >>> id.fromUnicode("      \\n x.y.z \\n")
        'x.y.z'

        """
        v = str(value.strip())
        self.validate(v)
        return v


class DottedName(BytesLine):
    """Dotted name field.

    Values of DottedName fields must be Python-style dotted names.
    """

    def __init__(self, *args, **kw):
        """
        >>> DottedName(min_dots=-1)
        Traceback (most recent call last):
        ...
        ValueError: min_dots cannot be less than zero

        >>> DottedName(max_dots=-1)
        Traceback (most recent call last):
        ...
        ValueError: max_dots cannot be less than min_dots

        >>> DottedName(max_dots=1, min_dots=2)
        Traceback (most recent call last):
        ...
        ValueError: max_dots cannot be less than min_dots

        >>> dotted_name = DottedName(max_dots=1, min_dots=1)

        >>> dotted_name = DottedName(max_dots=1)
        >>> dotted_name.min_dots
        0

        >>> dotted_name = DottedName(min_dots=1)
        >>> dotted_name.max_dots
        >>> dotted_name.min_dots
        1
        """
        self.min_dots = int(kw.pop("min_dots", 0))
        if self.min_dots < 0:
            raise ValueError("min_dots cannot be less than zero")
        self.max_dots = kw.pop("max_dots", None)
        if self.max_dots is not None:
            self.max_dots = int(self.max_dots)
            if self.max_dots < self.min_dots:
                raise ValueError("max_dots cannot be less than min_dots")
        super(DottedName, self).__init__(*args, **kw)

    def _validate(self, value):
        """
        >>> dotted_name = DottedName(__name__='test')
        >>> dotted_name.validate("a.b.c")
        >>> dotted_name.validate("a")
        >>> dotted_name.validate("   a   ")
        Traceback (most recent call last):
        ...
        ValidationError: ('invalid dotted name', '   a   ')

        >>> dotted_name = DottedName(__name__='test', min_dots=1)
        >>> dotted_name.validate('a.b')
        >>> dotted_name.validate('a.b.c.d')
        >>> dotted_name.validate('a')
        Traceback (most recent call last):
        ...
        ValidationError: ('too few dots; 1 required', 'a')

        >>> dotted_name = DottedName(__name__='test', max_dots=0)
        >>> dotted_name.validate('a')
        >>> dotted_name.validate('a.b')
        Traceback (most recent call last):
        ...
        ValidationError: ('too many dots; no more than 0 allowed', 'a.b')

        >>> dotted_name = DottedName(__name__='test', max_dots=2)
        >>> dotted_name.validate('a')
        >>> dotted_name.validate('a.b')
        >>> dotted_name.validate('a.b.c')
        >>> dotted_name.validate('a.b.c.d')
        Traceback (most recent call last):
        ...
        ValidationError: ('too many dots; no more than 2 allowed', 'a.b.c.d')

        >>> dotted_name = DottedName(__name__='test', max_dots=1, min_dots=1)
        >>> dotted_name.validate('a.b')
        >>> dotted_name.validate('a')
        Traceback (most recent call last):
        ...
        ValidationError: ('too few dots; 1 required', 'a')
        >>> dotted_name.validate('a.b.c')
        Traceback (most recent call last):
        ...
        ValidationError: ('too many dots; no more than 1 allowed', 'a.b.c')

        """
        super(DottedName, self)._validate(value)
        if not _isdotted(value):
            raise ValidationError("invalid dotted name", value)
        dots = value.count(".")
        if dots < self.min_dots:
            raise ValidationError("too few dots; %d required" % self.min_dots,
                                  value)
        if self.max_dots is not None and dots > self.max_dots:
            raise ValidationError("too many dots; no more than %d allowed"
                                  % self.max_dots,
                                  value)

    def fromUnicode(self, value):
        v = str(value.strip())
        self.validate(v)
        return v
