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
$Id: _bootstrapfields.py,v 1.20 2003/07/28 22:22:21 jim Exp $
"""
__metaclass__ = type

import warnings

from zope.interface import Attribute, providedBy, implements
from zope.schema.interfaces import StopValidation, ValidationError
from zope.schema.interfaces import IFromUnicode
from zope.schema._schema import getFields
from zope.schema import errornames

class ValidatedProperty:

    def __init__(self, name, check=None):
        self._info = name, check

    def __set__(self, inst, value):
        name, check = self._info
        if value is not None:
            if check is not None:
                check(inst, value)
            else:
                inst.validate(value)
        inst.__dict__[name] = value

class Field(Attribute):

    # Type restrictions, if any
    _type = None
    context = None

    # if input for this Field is missing, and that's ok, then this is the
    # value to use
    missing_value = None

    # Note that the "order" field has a dual existance:
    # 1. The class variable Field.order is used as a source for the
    #    monotonically increasing values used to provide...
    # 2. The instance variable self.order which provides a
    #    monotonically increasing value that tracks the creation order
    #    of Field (including Field subclass) instances.
    order = 0

    constraint = None
    default = ValidatedProperty('default')

    def __init__(self, __name__='', __doc__='',
                 title=u'', description=u'',
                 required=True, readonly=False, constraint=None, default=None,
                 ):
        """Pass in field values as keyword parameters.


        Generally, you want to pass either a title and description, or
        a doc string.  If you pass no doc string, it will be computed
        from the title and description.  If you pass a doc string that
        follows the Python coding style (title line separated from the
        body by a blank line), the title and description will be
        computed from the doc string.  Unfortunately, the doc string
        must be passed as a positional argument.

        Here are some examples:

        >>> f = Field()
        >>> f.__doc__, f.title, f.description
        ('', u'', u'')

        >>> f = Field(title=u"sample")
        >>> f.__doc__, f.title, f.description
        (u'sample', u'sample', u'')

        >>> f = Field(title=u"sample", description=u"blah blah\\nblah")
        >>> f.__doc__, f.title, f.description
        (u'sample\\n\\nblah blah\\nblah', u'sample', u'blah blah\\nblah')

        >>> f = Field(__doc__='''sample
        ...
        ...    blah blah
        ...    blah
        ...    ''')
        >>> f.__doc__, f.title
        ('sample\\n\\n   blah blah\\n   blah\\n   ', u'sample')
        >>> f.description
        u'   blah blah\\n   blah\\n'

        >>> f = Field(title=u"sample", description=u"blah blah",
        ...           __doc__="xxx")
        >>> f.__doc__, f.title, f.description
        ('xxx', u'sample', u'blah blah')

        """

        if not __doc__:
            if title:
                if description:
                    __doc__ = "%s\n\n%s" % (title, description)
                else:
                    __doc__ = title
            elif description:
                __doc__ = description
        else:
            doc = __doc__.strip().split('\n')
            if (not title and not description
                and (len(doc) == 1 or not doc[1].strip())):
                title = unicode(doc[0])
                description = u'\n'.join(doc[2:])+u'\n'

        super(Field, self).__init__(__name__, __doc__)
        self.title = title
        self.description = description
        self.required = required
        self.readonly = readonly
        if constraint is not None:
            self.constraint = constraint
        self.default = default

        # Keep track of the order of field definitions
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
        for interface in providedBy(self):
            names.update(getFields(interface))

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

    def get(self, object):
        return getattr(object, self.__name__)

    def query(self, object, default=None):
        return getattr(object, self.__name__, default)

    def set(self, object, value):
        if self.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.__name__,
                               object.__class__.__module__,
                               object.__class__.__name__))
        setattr(object, self.__name__, value)

class Container(Field):

    def _validate(self, value):
        super(Container, self)._validate(value)

        if not hasattr(value, '__contains__'):
            try:
                iter(value)
            except TypeError:
                raise ValidationError(errornames.NotAContainer, value)


class Iterable(Container):

    def _validate(self, value):
        super(Iterable, self)._validate(value)

        # See if we can get an iterator for it
        try:
            iter(value)
        except TypeError:
            raise ValidationError(errornames.NotAnIterator, value)


class Orderable:
    """Values of ordered fields can be sorted.

    They can be restricted to a range of values.

    Orderable is a mixin used in combination with Field.
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


class MinMaxLen:
    """Expresses constraints on the length of a field.

    MinMaxLen is a mixin used in combination with Field.
    """
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


class Enumerated:
    """Enumerated fields can have a value found in a constant set of
    values given by the field definition.

    Enumerated is a mixin used in combination with Field.
    """

    def __init__(self, allowed_values=None, default=None, **kw):
        # Set allowed_values to None so that we can validate if
        # one of the super methods invoke validation.
        self.__dict__['allowed_values'] = None
        super(Enumerated, self).__init__(**kw)
        if allowed_values is not None:
            self.allowed_values = allowed_values

        # We've taken over setting default so it can be limited by min
        # and max.
        self.default = default

    def allowed_values(self, values):
        # This method checks that each of the given allowed values
        # are valid potential values.

        if not values:
            return

        # Reset current value of allowed_values to not constrain allowed
        # values. If we didn't do this, we'd only be able to allow a subset
        # of the values currently allowed.
        old_allowed = getattr(self, 'allowed_values', None)
        self.allowed_values = None
        try:
            for value in values:
                self.validate(value)
        finally:
            # restore the old value
            self.allowed_values = old_allowed

    allowed_values = ValidatedProperty('allowed_values', allowed_values)

    def _validate(self, value):
        super(Enumerated, self)._validate(value)
        if self.allowed_values:
            if not value in self.allowed_values:
                raise ValidationError(errornames.InvalidValue, value,
                                      self.allowed_values)

class Text(Enumerated, MinMaxLen, Field):
    """A field containing text used for human discourse."""
    _type = unicode

    implements(IFromUnicode)

    def __init__(self, *args, **kw):
        if (  kw.get("allowed_values") is not None
              and self.__class__ in (Text, TextLine)):
            clsname = self.__class__.__name__
            warnings.warn("Support for allowed_values will be removed from %s;"
                          " use Enumerated%s instead" % (clsname, clsname),
                          DeprecationWarning, stacklevel=2)
        super(Text, self).__init__(*args, **kw)

    def fromUnicode(self, str):
        """
        >>> t = Text(constraint=lambda v: 'x' in v)
        >>> t.fromUnicode("foo x spam")
        Traceback (most recent call last):
        ...
        ValidationError: (u'Wrong type', 'foo x spam', <type 'unicode'>)
        >>> t.fromUnicode(u"foo x spam")
        u'foo x spam'
        >>> t.fromUnicode(u"foo spam")
        Traceback (most recent call last):
        ...
        ValidationError: (u'Constraint not satisfied', u'foo spam')
        """
        self.validate(str)
        return str

class TextLine(Text):
    """A text field with no newlines."""

    def constraint(self, value):
        return '\n' not in value and '\r' not in value

class EnumeratedTextLine(TextLine):
    """TextLine with a value from a list of allowed values."""

class Password(TextLine):
    """A text field containing a text used as a password."""

class Bool(Field):
    """A field representing a Bool."""
    _type = type(True)

class Int(Enumerated, Orderable, Field):
    """A field representing an Integer."""
    _type = int, long

    implements(IFromUnicode)

    def __init__(self, *args, **kw):
        if (  kw.get("allowed_values") is not None
              and self.__class__ is Int):
            clsname = self.__class__.__name__
            warnings.warn("Support for allowed_values will be removed from %s;"
                          " use Enumerated%s instead" % (clsname, clsname),
                          DeprecationWarning, stacklevel=2)
        super(Int, self).__init__(*args, **kw)

    def fromUnicode(self, str):
        """
        >>> f = Int()
        >>> f.fromUnicode("125")
        125
        >>> f.fromUnicode("125.6")
        Traceback (most recent call last):
        ...
        ValueError: invalid literal for int(): 125.6
        """
        v = int(str)
        self.validate(v)
        return v

class EnumeratedInt(Int):
    """A field representing one of a selected set of Integers."""
