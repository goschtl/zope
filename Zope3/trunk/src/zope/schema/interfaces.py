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
"""Schema interfaces and exceptions

$Id: interfaces.py,v 1.5 2003/03/25 11:47:56 tseaver Exp $
"""
from zope.interface import Interface

class StopValidation(Exception):
    """This exception is raised, if the validation is done for sure early.
    Note that this exception should be always caught, since it is just a
    way for the validator to save time."""
    pass


class ValidationError(Exception):
    """If some check during the Validation process fails, this exception is
    raised."""

    def __cmp__(self, other):
        return cmp(self.args, other.args)

    def __repr__(self):
        return ' '.join(map(str, self.args))

# Delay these imports to avoid circular import problems
from zope.schema._bootstrapfields import Field, Text, TextLine, Bool, Int
from zope.schema._bootstrapfields import Container, Iterable


class IField(Interface):
    """Basic Schema Field Interface.

    Fields are used for Interface specifications.  They at least provide
    a title, description and a default value.  You can also
    specify if they are required and/or readonly.

    The Field Interface is also used for validation and specifying
    constraints.

    We want to make it possible for a IField to not only work
    on its value but also on the object this value is bound to.
    This enables a Field implementation to perform validation
    against an object which also marks a certain place.

    Note that many fields need information about the object
    containing a field. For example, when validating a value to be
    set as an object attribute, it may be necessary for the field to
    introspect the object's state. This means that the field needs to
    have access to the object when performing validation.

    We haven't really decided on the best way to approach providing
    access to objects in field methods and properties. We've thought
    of three approaches:

    1. Always pass the object:

         field.validate(value, object)

    2. Bind the field to the object with a context wrapper:

         field = ContextWrapper(field, object)
         field.validate(value)

    3. Provide a specialized binding protocol:

         bound = field.bind(object)
         bound.validate(value)

    Options 2 and 3 allow us to use properties, but require an extra
    binding step.

    Option 1 and 3 will require a significant refactoring.

    Option 2 requires us to make field methods, or at least the
    validate method into ContextMethods, which is a bit intrusive.

    For now, we will use option 3.

    """

    def bind(object):
        """return a copy of this field which is bound to an object.

        The copy of the Field will have the 'context' attribute set
        to 'object'.  This way a Field can implement more complex
        checks involving the object and its location.

        Many fields don't need to be bound. Only fields that condition
        validation or properties on an object containing the field
        need to be bound.
        """

    title = TextLine(
        title=u"Title",
        description=u"A short summary or label",
        default=u"",
        required=False,
        )

    description = Text(
        title=u"Description",
        description=u"A description of the field",
        default=u"",
        required=False,
        )

    required = Bool(
        title=u"Required",
        description=(
        u"tells whether a field requires its value to exist."),
        default=True)

    readonly = Bool(
        title=u"Read Only",
        description=u"Read-only.", # XXX what is this?
        required=False,
        default=False)

    default = Field(
        title=u"default field value if no value is present",
        description=u"""The field default value may be None or a legal
                        field value"""
        )

    def constraint(value):
        u"""check a customized contraint on the value.

        You can implement this method with your Field to
        require a certain constraint.  This relaxes the need
        to inherit/subclass a Field you to add a simple contraint.
        Returns true if the given value is within the Field's contraint.
        """

    def validate(value):
        u"""Validate that the given value is a valid field value.

        Returns nothing but raises an error if the value is invalid.
        It checks everything specific to a Field and also checks
        with the additional constraint.
        """

    order = Int(
        title=u"Field Order",
        description=u"""\
        The order attribute can be used to determine the order in
        which fields in a schema were defined. If one field is created
        after another (in the same thread), its order will be
        greater.

        (Fields in separate threads could have the same order.)
        """,
        required=True,
        readonly=True,
        )


class IIterable(IField):
    u"""Fields with a value that can be iterated over.

    The value needs to follow the python __iter__ protocol.
    """

class IContainer(IField):
    u"""Fields whose value allows an 'x in value' check.

    The Value needs to have a conventional __contains__ method.
    """

class IOrderable(IField):
    u"""a Field requiring its value to be orderable.

    The value needs to have a conventional __cmp__ method.
    """

class ILen(IField):
    u"""a Field requiring its value to have a length.

    The value needs to have a conventional __len__ method.
    """

class IMinMax(IOrderable):
    u"""a Field requiring its value to be between min and max.

    This also means that the value needs to support the IOrderable interface.
    """

    min = Field(
        title=u"Start of the range",
        required=False,
        default=None
        )

    max = Field(
        title=u"End of the range (excluding the value itself)",
        required=False,
        default=None
        )


class IMinMaxLen(ILen):
    u"""a Field requiring the length of its value to be within a range"""

    min_length = Int(
        title=u"Minimum length",
        description=u"""\
        Value after whitespace processing cannot have less than
        min_length characters. If min_length is None, there is
        no minimum.
        """,
        required=False,
        min=0, # needs to be a positive number
        default=0)

    max_length = Int(
        title=u"Maximum length",
        description=u"""\
        Value after whitespace processing cannot have greater
        or equal than max_length characters. If max_length is
        None, there is no maximum.""",
        required=False,
        min=0, # needs to be a positive number
        default=None)

class IValueSet(IField):
    u"""Field whose value is contained in a predefined set"""

    allowed_values = Container(
        title=u"Allowed Values",
        description=u"""\
        Only values specified here can be values of this field.
        If the list is empty, then there are no further
        restictions.""",
        required=False)

class IBool(IField):
    u"""a Boolean Field."""

class IBytes(IMinMaxLen, IValueSet, IIterable):
    u"""a Field containing a byte string (like the python str).

    The value might be contrained to be with length limits, or
    be within a set of values.
    """

class IBytesLine(IBytes):
    u"""a Field containing a byte string without newlines."""

class IText(IMinMaxLen, IValueSet, IIterable):
    u"""a Field containing a unicode string."""

class ITextLine(IText):
    u"""a Field containing a unicode string without newlines."""

class IPassword(ITextLine):
    u"""a Field containing a unicode string without newlines that is a password."""

class IInt(IMinMax, IValueSet):
    u"""a Field containing an Integer Value."""

class IFloat(IMinMax, IValueSet):
    u"""a Field containing a Float."""

class IDatetime(IMinMax, IValueSet):
    u"""a Field containing a DateTime."""

def _fields(values):
    for value in values:
        if not IField.isImplementedBy(value):
            return False
    return True

class ISequence(IMinMaxLen, IIterable):
    u"""a Field containing a Sequence value.

    The Value must be iterable and may have a min_length/max_length.
    """

    value_types = Iterable(
        title=u"Value Types",
        description=(
        u"""\
        If set to a non-empty value, field value items must conform to one
        of the given types, which are expressed via fields.
        """),
        required=False,
        constraint=_fields,
        )

class ITuple(ISequence):
    u"""a Field containing a conventional tuple."""

class IList(ISequence):
    u"""a Field containing a conventional list."""

class IDict(IMinMaxLen, IIterable):
    u"""a Field containing a conventional dict.

    the key_types and value_types field allow specification
    of restrictions for the dict.
    """

    key_types = Iterable(
        title=u"Value Types",
        description=u"""\
        If set to a non-empty value, field value keys must conform to one
        of the given types, which are expressed via fields.
        """,
        constraint=_fields,
        required=False,
        )

    value_types = Iterable(
        title=u"Value Types",
        description=(
        u"""\
        If set to a non-empty value, field value values must conform to one
        of the given types, which are expressed via fields.
        """),
        constraint=_fields,
        required=False,
        )
