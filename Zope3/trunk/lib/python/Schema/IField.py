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

$Id: IField.py,v 1.2 2002/07/14 13:32:53 srichter Exp $
"""
from Interface import Interface
import _Field as Field

class IField(Interface):
    """All fields conform to this schema. Note that the interpretation
    of 'required' is up to each field by itself. For some fields, such as
    IBoolean, requiredness settings may make no difference.
    """

    title = Field.String(
        title="Title",
        description="Title.",
        default=""
        )
    
    description = Field.String(
        title="Description",
        description="Description.",
        default="",
        required=0)

    readonly = Field.Boolean(
        title="Read Only",
        description="Read-only.",
        default=0)
    
    required = Field.Boolean(
        title="Required",
        description="Required.",
        default=1)


class ISingleValueField(IField):
    """This field consists always only of one value and it not a homogeneous
    container, like a list. Note that structures and instances of classes
    might or might not be ISingleValueFields."""
    
    allowed_values = Field.Tuple(
        title="Allowed Values",
        description="Only values specified here can be values of this field. "
                    "If the list is empty, then there are no further "
                    "restictions.",
        required=0,
        default=())
        

    
class IBoolean(ISingleValueField):
    """Describes the footprint of a Boolean variable."""

    default = Field.Boolean(
        title="Default",
        description="Default.",
        default=0)


class IString(ISingleValueField):
    """Describes the footprint of a String variable."""

    default = Field.String(
        title="Default",
        description="Default.",
        default="")
    
    whitespace = Field.String(
        title="Whitespace",
        description="preserve: whitespace is preserved."
                    "replace: all occurences of tab, line feed and "
                    "carriage return are replaced with space characters. "
                    "collapse: first process as in 'replace', then "
                    "collapse all spaces to a single space, and strip any "
                    "spaces from front and back."
                    "strip: strip off whitespace from front and back.",
        allowed_values=("preserve", "replace", "collapse", "strip"),
        default="strip")

    min_length = Field.Integer(
        title="Minimum length",
        description=("Value after whitespace processing cannot have less than "
                     "min_length characters. If min_length is None, there is "
                     "no minimum."),
        required=0,
        min=0, # needs to be a positive number
        default=0)

    max_length = Field.Integer(
        title="Maximum length",
        description=("Value after whitespace processing cannot have greater "
                     "or equal than max_length characters. If max_length is "
                     "None, there is no maximum."),
        required=0,
        min=0, # needs to be a positive number
        default=None)

    
class IInteger(ISingleValueField):
    """Describes the footprint of an Integer variable."""

    default = Field.Integer(
        title="Default",
        description="Default.",
        default=0)
    
    min = Field.Integer(
        title="Minimum",
        description="The minimal numerical value accepted. If min is None, "
                    "there is no minimum.",
        required=0,
        default=0)

    max = Field.Integer(
        title="Maximum",
        description="The masximal numerical value accepted. If min is None, "
                    "there is no minimum.",
        required=0,
        default=None)
    
    
class IFloat(ISingleValueField):
    """Describes the footprint of a Float variable."""

    default = Field.Float(
        title="Default",
        description="Default.",
        default=0)
    
    min = Field.Float(
        title="Minimum",
        description="The minimal numerical value accepted. If min is None, "
                    "there is no minimum.",
        required=0,
        default=0)

    max = Field.Float(
        title="Maximum",
        description="The masximal numerical value accepted. If min is None, "
                    "there is no minimum.",
        required=0,
        default=None)
    
    decimals = Field.Integer(
        title="Decimal Places",
        description="Defines the amount of decimal places the floating point "
                    "can have. This value is also know as precision. If the "
                    "value is None, no precision is required.",
        required=0,
        default=None)


class IMultipleValueField(IField):
    """This field will contain some sort of collection of objects whose types
    can be often defined through a finite set of types."""

    value_types = Field.Tuple(
        title="Value Types",
        description="Defines the value types that are allowed in the list. "
                    "If the list is empty, then all types are allowed.",
        required=0,
        default=())

    min_values = Field.Integer(
        title="Minimum amount of values",
        description="The minimum amount of values in the list. If min_values "
                    "is None, there is no minimum.",
        min=0,
        required=0,
        default=0)

    max_values = Field.Integer(
        title="Maximum amount of values",
        description="The maximum amount of values in the list. If max_values "
                    "is None, there is no maximum.",
        min=0,
        required=0,
        default=None)


class ITuple(IMultipleValueField):
    """Describes the footprint of a Tuple variable."""

    default = Field.Tuple(
        title="Default",
        description="Default.",
        default=())    


class IList(ITuple):
    """Describes the footprint of a List variable."""

    default = Field.List(
        title="Default",
        description="Default.",
        default=[])


class IDictionary(IMultipleValueField):
    """Describes the footprint of a Dictionary variable."""

    default = Field.Dictionary(
        title="Default",
        description="Default.",
        default={})    

    key_types = Field.Tuple(
        title="Value Types",
        description="Defines the key types that are allowed in the "
                    "dictionary. If the list is empty, then all types "
                    "are allowed.",
        required=0,
        default=())
