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
$Id: _Schema.py,v 1.8 2002/07/25 22:09:30 faassen Exp $
"""
from Interface import Interface
import Validator
from Schema.Exceptions import \
     StopValidation, ValidationError, ValidationErrorsAll


class Schema(Interface):
    """This is really just a marker class, but it seems more userfriendly
    this way."""
    

# validate functions either return silently, or raise a ValidationError
# or in case of the validate*All functions, a ValidationErrosAll exception.
# this should somehow be stated in an interface.

def validateMapping(schema, values):
    """Pass in field values in mapping and validate whether they
    conform to schema. Stop at first error.
    """
    from IField import IField
    for name in schema.names(1):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            attr.validate(values.get(name))

def validateMappingAll(schema, values):
    """Pass in field values in mapping and validate whether they
    conform to schema.
    """
    errors = []
    from IField import IField
    for name in schema.names(1):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            try:
                attr.validate(values.get(name))
            except ValidationError, e:
                errors.append((name, e))
    if errors:
        raise ValidationErrorsAll, errors

# Now we can create the interesting interfaces and wire them up:
def wire():
    from Interface.Implements import implements

    from IField import IField
    from _Field import Field
    implements(Field, IField, 0)
    Field.validator = Validator.RequiredValidator

    from IField import IBool
    from _Field import Bool
    implements(Bool, IBool, 0)
    Bool.validator = Validator.BoolValidator

    from IField import IStr
    from _Field import Str
    implements(Str, IStr, 0)
    Str.validator = Validator.StrValidator

    from IField import IInt
    from _Field import Int
    implements(Int, IInt, 0)
    Int.validator = Validator.IntValidator

    from IField import IFloat
    from _Field import Float
    implements(Float, IFloat, 0)
    Float.validator = Validator.FloatValidator

    from IField import ITuple
    from _Field import Tuple
    implements(Tuple, ITuple, 0)
    Tuple.validator = Validator.TupleValidator

    from IField import IList
    from _Field import List
    implements(List, IList, 0)
    List.validator = Validator.ListValidator

    from IField import IDict
    from _Field import Dict
    implements(Dict, IDict, 0)
    Dict.validator = Validator.DictValidator


wire()
del wire

