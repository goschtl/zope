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
$Id: _bootstrapFields.py,v 1.2 2002/09/18 15:05:51 jim Exp $
"""
__metaclass__ = type

from Interface.Attribute import Attribute
from Exceptions import StopValidation, ValidationError
import ErrorNames

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
    order = 0l

    constraint = None
    default = ValidatedProperty('default')
    
    def __init__(self, __name__='', __doc__='',
                 title=u'', description=u'',
                 required=False, readonly=False, constraint=None, default=None,
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
        self.constraint = constraint
        self.default = default

        # Keep track of the order of field definition
        Field.order += 1
        self.order = Field.order

        
    def validate(self, value):
        if value is None:
            if self.required:
                raise ValidationError(ErrorNames.RequiredMissing)
        else:
            try:
                self._validate(value)
            except StopValidation:
                pass
        
    def _validate(self, value):

        if self._type is not None and not isinstance(value, self._type):
            raise ValidationError(ErrorNames.WrongType, value, self._type)

        if self.constraint is not None and not self.constraint(value):
            raise ValidationError(ErrorNames.ConstraintNotSatisfied, value)


class Container(Field):

    def _validate(self, value):
        super(Container, self)._validate(value)

        if not hasattr(value, '__contains__'):
            try:
                iter(value)
            except:
                raise ValidationError(ErrorNames.NotAContainer, value)
                
                
class Iteratable(Container):

    def _validate(self, value):
        super(Iteratable, self)._validate(value)

        # See if we can get an iterator for it
        try:
            iter(value)
        except:
            raise ValidationError(ErrorNames.NotAnIterator, value)


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
            raise ValidationError(ErrorNames.TooSmall, value, self.min)

        if self.max is not None and value > self.max:
            raise ValidationError(ErrorNames.TooBig, value, self.max)

_int_types = int, long
class Sized(Field):
    min_length = 0
    max_length = None

    def __init__(self, min_length=0, max_length=None, **kw):
        self.min_length = min_length
        self.max_length = max_length
        super(Sized, self).__init__(**kw)

    def _validate(self, value):
        super(Sized, self)._validate(value)

        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError(ErrorNames.TooShort, value, self.min_length)

        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError(ErrorNames.TooLong, value, self.max_length)
        

class Enumeratable(Field):

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
        self.allowed_values = None
        super(Enumeratable, self).__init__(**kw)
        self.allowed_values = allowed_values

        # We've taken over setting default so it can be limited by min
        # and max.
        self.default = default

    def _validate(self, value):
        super(Enumeratable, self)._validate(value)

        if self.allowed_values:
            if not value in self.allowed_values:
                raise ValidationError(ErrorNames.InvalidValue)


class Text(Sized, Enumeratable):
    """A field representing a Str."""
    _type = unicode

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

class Int(Enumeratable, Orderable):
    """A field representing a Integer."""
    _type = int, long
