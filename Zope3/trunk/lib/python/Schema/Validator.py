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
$Id: Validator.py,v 1.1 2002/07/14 13:32:53 srichter Exp $
"""
from types import ListType, TupleType
ListTypes = (ListType, TupleType)
from Schema.IValidator import IValidator
from Schema.IField import *
from Schema._Field import *

from Schema.Exceptions import StopValidation, ValidationError
import ErrorNames

class Validator:
    """Validator base class"""
    __implements__ =  IValidator

    def __init__(self, field):
        self.field = field
    
    def getDescription(self):
        return self.__doc__

    def validate(self, value):
        'See Schema.IValidator.IValidator'
        return value


class TypeValidator(Validator):
    """Check whether the value is of the correct type."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        t = self.field.type
        if t is not None and value is not None and not isinstance(value, t):
            raise ValidationError, ErrorNames.WrongType
        return value

class RequiredValidator(Validator):
    """If no value was passed, check whether the field was required."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        if value is None:
            if self.field.required:
                raise ValidationError, ErrorNames.RequiredMissing
            else:
                # we are done with validation for sure
                raise StopValidation
        return value

class StringRequiredValidator(Validator):
    """Empty Strings are not acceptable for a required field."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        if self.field.required and value == '':
            raise ValidationError, ErrorNames.RequiredEmptyString
        return value

class MinimumLengthValidator(Validator):
    """Check that the length is larger than the minimum value."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        length = len(value)
        if self.field.min_length is not None and \
               length < self.field.min_length:
            raise ValidationError, ErrorNames.TooShort
        return value

class MaximumLengthValidator(Validator):
    """Check that the length is smaller than the maximum value."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        length = len(value)
        if self.field.max_length is not None and \
               length > self.field.max_length:
            raise ValidationError, ErrorNames.TooLong
        return value

class MinimumValueValidator(Validator):
    """Check that the value is larger than the minimum value."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        if self.field.min is not None and value < self.field.min:
            raise ValidationError, ErrorNames.TooSmall
        return value

class MaximumValueValidator(Validator):
    """Check that the value is smaller than the maximum value."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        if self.field.max is not None and value > self.field.max:
            raise ValidationError, ErrorNames.TooBig
        return value

class AllowedValuesValidator(Validator):
    """Check whether the value is in one of the allowed values."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        allowed = self.field.allowed_values
        if len(allowed) > 0 and value not in allowed:
            raise ValidationError, ErrorNames.InvalidValue
        return value

class WhitespaceValidator(Validator):
    """Check and convert the whitespaces of the value."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        option = self.field.whitespaces 
        if option in ('replace', 'collapse'):
            value = value.replace('\t', ' ')
            value = value.replace('\r', ' ')
            value = value.replace('\n', ' ')
        if option == 'collapse':
            value = ' '.join(value.split())
        if option == 'strip':
            value = value.strip()
        return value

class DecimalsValidator(Validator):
    """Check that the float value has the right precision."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        value_str = str(value)
        try:
            decimals = len(value_str.split('.')[1])
        except IndexError:
            decimals = 0
        if self.field.decimals and  decimals > self.field.decimals:
            raise ValidationError, ErrorNames.TooManyDecimals
        return value

def _flatten(list):
    out = []
    for elem in list:
        if isinstance(elem, ListTypes):
            out += _flatten(elem)
        else:
            out.append(elem)
    return out

class ListValueTypeValidator(Validator):
    """Check that the values in the value have the right type."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        if self.field.value_types:
            types = map(lambda field: field.type, self.field.value_types)
            types = tuple(_flatten(types))
            for val in value:
                if not isinstance(val, types):
                    raise ValidationError, ErrorNames.WrongContainedType
        return value

class MinimumAmountOfItemsValidator(Validator):
    """Check whether the list contains enough items."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        if self.field.min_values and value is not None and \
               len(value) < self.field.min_values:
            raise ValidationError, ErrorNames.NotEnoughElements
        return value

class MaximumAmountOfItemsValidator(Validator):
    """Check whether the list contains not too many items."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        if self.field.max_values and len(value) > self.field.max_values:
            raise ValidationError, ErrorNames.TooManyElements
        return value

class DictKeyTypeValidator(Validator):
    """Check that the values in the value have the right type."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        keys = value.keys()
        field = List(id='temp', title='temp',
                     value_types=self.field.key_types)
        validator = ListValueTypeValidator(field)
        validator.validate(keys)
        return value

class DictValueTypeValidator(Validator):
    """Check that the values in the value have the right type."""
    def validate(self, value):
        'See Schema.IValidator.IValidator'
        values = value.values()
        field = List(id='temp', title='temp',
                     value_types=self.field.value_types)
        validator = ListValueTypeValidator(field)
        validator.validate(values)
        return value

class ContainerValidator(Validator):
    """ """
    validators = [TypeValidator, RequiredValidator]

    def validate(self, value):
        'See Schema.IValidator.IValidator'        
        for validator in self.validators:
            try:
                value = validator(self.field).validate(value)
            except StopValidation:
                return value
        return value

class SingleValueValidator(ContainerValidator):
    """Validator for Single Value Fields"""
    validators = ContainerValidator.validators + [AllowedValuesValidator] 
    
class StringValidator(SingleValueValidator):
    """Completely validates a String Field."""
    validators = SingleValueValidator.validators + [StringRequiredValidator,
                                                    WhitespaceValidator,
                                                    MinimumLengthValidator,
                                                    MaximumLengthValidator]

class BooleanValidator(SingleValueValidator):
    """Completely validates a Boolean Field."""

class IntegerValidator(SingleValueValidator):
    """Completely validates a Integer Field."""
    validators = SingleValueValidator.validators + [MinimumValueValidator,
                                                    MaximumValueValidator]

class FloatValidator(SingleValueValidator):
    """Completely validates a Float Field."""
    validators = SingleValueValidator.validators + [MinimumValueValidator,
                                                    MaximumValueValidator,
                                                    DecimalsValidator]

class MultiValueValidator(ContainerValidator):
    """Validator for Single Value Fields"""
    validators = ContainerValidator.validators + [
        ListValueTypeValidator,
        MinimumAmountOfItemsValidator, MaximumAmountOfItemsValidator] 

class TupleValidator(MultiValueValidator):
    """Completely validates a Tuple Field."""

class ListValidator(TupleValidator):
    """Completely validates a List Field."""

class DictionaryValidator(MultiValueValidator):
    """Completely validates a Dictionary Field."""
    validators = ContainerValidator.validators + [
        DictKeyTypeValidator, DictValueTypeValidator,
        MinimumAmountOfItemsValidator, MaximumAmountOfItemsValidator] 

