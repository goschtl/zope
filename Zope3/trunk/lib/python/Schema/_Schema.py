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
$Id: _Schema.py,v 1.4 2002/07/14 13:32:53 srichter Exp $
"""
from Interface import Interface
import Validator
from Schema.Exceptions import \
     StopValidation, ValidationError, ValidationErrorsAll


class Schema(Interface):
    """This is really just a marker class, but it seems more userfriendly
    this way."""
    

def validateMapping(schema, values):
    """Pass in field values in mapping and validate whether they
    conform to schema. Stop at first error.
    """
    from IField import IField
    for name in schema.names(1):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            attr.validate(values.get(name))
    return 1

def validateMappingAll(schema, values):
    """Pass in field values in mapping and validate whether they
    conform to schema.
    """
    list = []
    from IField import IField
    for name in schema.names(1):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            try:
                attr.validate(values.get(name))
            except ValidationError, e:
                list.append((name, e))
    if list:
        raise ValidationErrorsAll, list
    return 1

# Now we can create the interesting interfaces and wire them up:
def wire():
    from Interface.Implements import implements

    from IField import IField
    from _Field import Field
    implements(Field, IField, 0)
    Field.validator = Validator.RequiredValidator

    from IField import IBoolean
    from _Field import Boolean
    implements(Boolean, IBoolean, 0)
    Boolean.validator = Validator.BooleanValidator

    from IField import IString
    from _Field import String
    implements(String, IString, 0)
    String.validator = Validator.StringValidator

    from IField import IInteger
    from _Field import Integer
    implements(Integer, IInteger, 0)
    Integer.validator = Validator.IntegerValidator

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

    from IField import IDictionary
    from _Field import Dictionary
    implements(Dictionary, IDictionary, 0)
    Dictionary.validator = Validator.DictionaryValidator


wire()
del wire

