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
$Id: _bootstrapfields.py,v 1.3 2003/01/09 14:13:18 jim Exp $
"""
__metaclass__ = type

from zope.interface import Attribute
from zope.interface.implements import visitImplements

from zope.schema.interfaces import StopValidation, ValidationError
from zope.schema._schema import getFields
from zope.schema import errornames

class ValidatedProperty:

    def __init__(self, name, check = None):
        self.__info  = name, check

    def __set__(self, inst, value):
        name, check = self.__info
        if value is not None:
            if check is not None:
                check(inst, value)
            else:
                inst.validate(value)
        inst.__dict__[name] = value

class Field(Attribute):

    # Type restrictions, if any
    _type = None
    order = 0
    context = None

    constraint = None
    default = ValidatedProperty('default')

    def __init__(self, __name__='', __doc__='',
                 title=u'', description=u'',
                 required=True, readonly=False, constraint=None, default=None,
                 ):
        """Pass in field values as keyword parameters."""


        if not __doc__:
            if title:
                if description:
                    __doc__ =  "%s\n\n%s" % (title, description)
                else:
                    __doc__ = title
            elif description:
                __doc__ = description

        super(Field, self).__init__(__name__, __doc__)
        self.title = title
        self.description = description
        self.required = required
        self.readonly = readonly
        if constraint is not None:
            self.constraint = constraint
        self.default = default

        # Keep track of the order of field definition
        Field.order += 1
        self.order = Field.order

    def bind(self, object):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)
        clone.context = object
        return clone

    def validate(self, value):
        if value is None:
            if self.required:
                raise ValidationError(errornames.RequiredMissing)
        else:
            try:
                self._validate(value)
            except StopValidation:
                pass

    def __eq__(self, other):
        # should be the same type
        if type(self) != type(other):
            return False
        # should have the same properties
        names = {} # used as set of property names, ignoring values
        visitImplements(self.__implements__, self,
                        lambda interface: names.update(getFields(interface)))
        # order will be different always, don't compare it
        if 'order' in names:
            del names['order']
        for name in names:
            if getattr(self, name) != getattr(other, name):
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def _validate(self, value):

        if self._type is not None and not isinstance(value, self._type):
            raise ValidationError(errornames.WrongType, value, self._type)

        if self.constraint is not None and not self.constraint(value):
            raise ValidationError(errornames.ConstraintNotSatisfied, value)


class Container(Field):

    def _validate(self, value):
        super(Container, self)._validate(value)

        if not hasattr(value, '__contains__'):
            try:
                iter(value)
            except:
                raise ValidationError(errornames.NotAContainer, value)


class Iterable(Container):

    def _validate(self, value):
        super(Iterable, self)._validate(value)

        # See if we can get an iterator for it
        try:
            iter(value)
        except:
            raise ValidationError(errornames.NotAnIterator, value)


class Orderable(Field):
    """Values of ordered fields can be sorted

    They can be restricted to a range of values.
    """

    min = ValidatedProperty('min')
    max = ValidatedProperty('max')

    def __init__(self, min=None, max=None, default=None, **kw):

        # Set min and max to None so that we can validate if
        # one of the super methods invoke validation.
        self.min = None
        self.max = None

        super(Orderable, self).__init__(**kw)

        # Now really set min and max
        self.min = min
        self.max = max

        # We've taken over setting default so it can be limited by min
        # and max.
        self.default = default


    def _validate(self, value):
        super(Orderable, self)._validate(value)

        if self.min is not None and value < self.min:
            raise ValidationError(errornames.TooSmall, value, self.min)

        if self.max is not None and value > self.max:
            raise ValidationError(errornames.TooBig, value, self.max)

_int_types = int, long
class MinMaxLen(Field):
    min_length = 0
    max_length = None

    def __init__(self, min_length=0, max_length=None, **kw):
        self.min_length = min_length
        self.max_length = max_length
        super(MinMaxLen, self).__init__(**kw)

    def _validate(self, value):
        super(MinMaxLen, self)._validate(value)

        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(errornames.TooShort, value, self.min_length)

        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(errornames.TooLong, value, self.max_length)


class ValueSet(Field):

    def allowed_values(self, values):
        # Reset current value so it doesn't hose validation
        if not values:
            return

        old_allowed = getattr(self, 'allowed_values', None)
        self.allowed_values = None

        for value in values:

            try:
                self.validate(value)
            except:
                # restore the old value
                self.allowed_values = old_allowed
                raise

    allowed_values = ValidatedProperty('allowed_values', allowed_values)

    def __init__(self, allowed_values=None, default=None, **kw):

        # Set allowed_values to None so that we can validate if
        # one of the super methods invoke validation.
        self.__dict__['allowed_values'] = None
        super(ValueSet, self).__init__(**kw)
        if allowed_values is not None:
            self.allowed_values = allowed_values

        # We've taken over setting default so it can be limited by min
        # and max.
        self.default = default

    def _validate(self, value):
        super(ValueSet, self)._validate(value)

        if self.allowed_values:
            if not value in self.allowed_values:
                raise ValidationError(errornames.InvalidValue, value,
                                      self.allowed_values)


class Text(MinMaxLen, ValueSet):
    """A field containing text used for human discourse."""
    _type = unicode


class TextLine(Text):
    """A Text field with no newlines."""

    def constraint(self, value):
        # XXX we should probably use a more general definition of newlines
        return '\n' not in value


class Bool(Field):
    """A field representing a Bool."""

    try:
        if type(True) is int:
            # If we have True and it's an int, then pretend we're 2.2.0.
            raise NameError("True")
    except NameError:
        # Pre booleans
        _type = int
    else:
        _type = bool

class Int(ValueSet, Orderable):
    """A field representing a Integer."""
    _type = int, long

