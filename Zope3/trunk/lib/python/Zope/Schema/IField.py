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

$Id: IField.py,v 1.6 2002/10/04 18:24:55 jim Exp $
"""
from Interface import Interface

from _bootstrapFields import Field, Text, Bool, Int, Container, Iteratable

class IField(Interface):
    u"""Fields

    Fields are attribute specifications.
    """

    title = Text(
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
    u"""Describes the footprint of a Bytes variable."""

class IText(ISized, IEnumeratable, IIteratable):
    u"""Describes the footprint of a Str variable."""
    
class IInt(IEnumeratable, IOrderable):
    u"""Describes the footprint of an Int variable."""
        
class IFloat(IEnumeratable, IOrderable):
    u"""Describes the footprint of a Float variable."""
        
class IDatetime(IEnumeratable, IOrderable):
    u"""Describes the footprint of a datetime variable."""

def _fields(values):
    for value in values:
        if not IField.isImplementedBy(value):
            return 0
    return 1

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
