from Interface.Attribute import Attribute
from Interface.Implements import objectImplements

from Exceptions import StopValidation, ValidationError
import ErrorNames
#from _Schema import validate

class Field(Attribute):

    # we don't implement the same interface Attribute
    __implements__ = ()

    default = None
    required = 0

    def __init__(self, **kw):
        """
        Pass in field values as keyword parameters.
        """
        for key, value in kw.items():
            setattr(self, key, value)
        super(Field, self).__init__(self.title or 'no title')

    def validate(self, value):
        try:
            self._validate(value)
        except StopValidation:
            pass

    def _validate(self, value):
        if value is None:
            if self.required:
                raise ValidationError, ErrorNames.RequiredMissing
            else:
                # we are done with validation for sure
                raise StopValidation

class Str(Field):

    min_length = None
    max_length = None

    def _validate(self, value):
        super(Str, self)._validate(value)
        if self.required and value == '':
            raise ValidationError,ErrorNames.RequiredEmptyString
        length = len(value)
        if self.min_length is not None and length < self.min_length:
            raise ValidationError, ErrorNames.TooShort
        if self.max_length is not None and length >= self.max_length:
            raise ValidationError, ErrorNames.TooLong

class Bool(Field):

    def _validate(self, value):
        super(Bool, self)._validate(value)

class Int(Field):

    min = max = None

    def _validate(self, value):
        super(Int, self)._validate(value)
        if self.min is not None and value < self.min:
            raise ValidationError, ErrorNames.TooSmall
        if self.max is not None and value > self.max:
            raise ValidationError, ErrorNames.TooBig

