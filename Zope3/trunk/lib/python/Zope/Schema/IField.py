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
"""These are the interfaces for the common fields.

$Id: IField.py,v 1.10 2002/11/11 20:24:35 jim Exp $
"""
from Interface import Interface

from _bootstrapFields \
     import Field, Text, TextLine, Bool, Int, Container, Iteratable

class IField(Interface):
    u"""Fields

    Fields are attribute specifications. They specify the allowed
    values for object attributes, Field are typically defined in an
    interface. 

    XXX We need to think aboyt the following
    
    Note that many field need information about the object
    implementing a field. For example, when validating a value to be
    set as an object attribute, it may be necessary for the field to
    introspect the object's state. This meanss that the field needs to
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

         bound = field(object_
         bound.validate(value)

    Options 2 and 3 allow us to use properties, but require an extra
    binding step.
    
    Option 1 and 3 will require a significant refactoring.

    Option 2 requires us to make field methods, or at least the
    validate method into ContextMethods, which is a bit intrusive.

    For now, we will use option 3.  

    """

    def bind(object):
        """Bind the field to an object

        This is done by returning a copy of the field with a "context"
        attribute set to the object.

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
        u"An indication of whether the field value must be provided"),
        default=True)

    readonly = Bool(
        title="uRead Only",
        description=u"Read-only.", # XXX what is this?
        default=False)

    default = Field(
        title=u"The default field value",
        description=u"""The field default value may be None or a legal
                        field value"""
        )

    def constraint(value):
        u"""Optional vaue constraint

        Returns true is the value is legal, and false otherwise.

        This is typically specified as a constructor argument.
        """

    def validate(value):
        u"""Validate that the given value is a valid field entry.

        Returns nothing but raises an error if the value is invalid.
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

class IContainer(IField):
    u"""Fields with values that allow containment checks using the in operator

    Values include squences, iteratorable objects, and any objects
    that implement __contains__.
    """

class IIteratable(IContainer):
    u"""Fields with value that can be iterated over
    """

class IOrderable(IField):
    u"""Orderable values

    They can be restricted to a range of values by specifying a
    minimum and maximum value.
    """

    min = Field(
        title=u"The minimum allowable value",
        description=u"""\
        If this value is not None, then it must be a legal field value
        and all field values must be less than this valie.        
        """
        )

    max = Field(
        title=u"The maximum allowable value",
        description=u"""\
        If this value is not None, then it must be a legal field value
        and all field values must be greater than this valie.        
        """
        )

class ISized(IField):
    u"""Sized objects may have a minimum and maximum length
    """
    
    min_length = Int(
        title=u"Minimum length",
        description=u"""\
        Value after whitespace processing cannot have less than 
        min_length characters. If min_length is None, there is 
        no minimum.
        """,
        required=0,
        min=0, # needs to be a positive number
        default=0)

    max_length = Int(
        title=u"Maximum length",
        description=u"""\
        Value after whitespace processing cannot have greater
        or equal than max_length characters. If max_length is
        None, there is no maximum.""",
        required=0,
        min=0, # needs to be a positive number
        default=None)


class IEnumeratable(IField):
    u"""Fields with values that may be constrained to a set of values
    """
    
    allowed_values = Container(
        title=u"Allowed Values",
        description=u"""\
        Only values specified here can be values of this field.
        If the list is empty, then there are no further
        restictions.""",
        required=0)
            
class IBool(IField):
    u"""Describes the footprint of a Bool variable."""

class IBytes(ISized, IEnumeratable, IIteratable):
    u"""Describes the footprint of a Bytes variable"""

class ILine(IBytes):
    u"""Describes the footprint of a Bytes variable withouit newlines"""

class IText(ISized, IEnumeratable, IIteratable):
    u"""Describes the footprint of a Text variable."""

class ITextLine(IText):
    u"""Describes the footprint of a one-line Text variable."""
    
class IInt(IEnumeratable, IOrderable):
    u"""Describes the footprint of an Int variable."""
        
class IFloat(IEnumeratable, IOrderable):
    u"""Describes the footprint of a Float variable."""
        
class IDatetime(IEnumeratable, IOrderable):
    u"""Describes the footprint of a datetime variable."""

def _fields(values):
    for value in values:
        if not IField.isImplementedBy(value):
            return False
    return True

class ISequence(ISized, IIteratable):
    u"""Describes fields that can hold a sequence values

    These values may be constrained.
    """

    value_types = Iteratable(
        title=u"Value Types",
        description=(
        u"""\
        If set to a non-empty value, field value items must conform to one
        of the given types, which are expressed via fields.
        """),
        required=0,
        constraint=_fields,
        )


class ITuple(ISequence):
    u"""Describes the footprint of a Tuple variable."""

class IList(ISequence):
    u"""Describes the footprint of a List variable."""


class IDict(ISized, IIteratable):
    u"""Describes the footprint of a Dict variable."""

    key_types = Iteratable(
        title=u"Value Types",
        description=u"""\
        If set to a non-empty value, field value keys must conform to one
        of the given types, which are expressed via fields.
        """,
        constraint=_fields,
        required=0,
        )

    value_types = Iteratable(
        title=u"Value Types",
        description=(
        u"""\
        If set to a non-empty value, field value values must conform to one
        of the given types, which are expressed via fields.
        """),
        constraint=_fields,
        required=0,
        )
