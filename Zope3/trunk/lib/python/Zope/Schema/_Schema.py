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
$Id: _Schema.py,v 1.3 2002/09/11 22:06:41 jim Exp $
"""
from Interface import Interface
from Zope.Schema.Exceptions import ValidationError, ValidationErrorsAll
    
def getFields(schema):
    """Get all fields on a schema.
    """
    from IField import IField
    fields = {}
    for name in schema.names(1):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            fields[name] = attr
    return fields


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

