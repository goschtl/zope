##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Simple data type converters for form parsing, registered by name

$Id: $
"""

import re

newlines = re.compile('\r\n|\n\r|\r')

array_types = (list, tuple)

def field2string(v):
    if hasattr(v, 'read'):
        return v.read()
    if not isinstance(v, basestring):
        v = str(v)
    return v

def field2text(v):
    return newlines.sub("\n", field2string(v))

def field2required(v):
    test = field2string(v)
    if not test.strip():
        raise ValueError('No input for required field')
    return v

def field2int(v):
    if isinstance(v, array_types):
        return map(field2int, v)
    v = field2string(v)
    if not v:
        raise ValueError('Empty entry when integer expected')
    try:
        return int(v)
    except ValueError:
        raise ValueError("An integer was expected in the value '%s'" % v)

def field2float(v):
    if isinstance(v, array_types):
        return map(field2float, v)
    v = field2string(v)
    if not v:
        raise ValueError('Empty entry when float expected')
    try:
        return float(v)
    except ValueError:
        raise ValueError("A float was expected in the value '%s'" % v)

def field2long(v):
    if isinstance(v, array_types):
        return map(field2long, v)
    v = field2string(v)

    # handle trailing 'L' if present.
    if v and v[-1].upper() == 'L':
        v = v[:-1]
    if not v:
        raise ValueError('Empty entry when integer expected')
    try:
        return long(v)
    except ValueError:
        raise ValueError("A long integer was expected in the value '%s'" % v)

def field2tokens(v):
    return field2string(v).split()

def field2lines(v):
    if isinstance(v, array_types):
        return [field2string(item) for item in v]
    return field2text(v).splitlines()

def field2boolean(v):
    return bool(v)

type_converters = {
    'float':    field2float,
    'int':      field2int,
    'long':     field2long,
    'string':   field2string,
    'required': field2required,
    'tokens':   field2tokens,
    'lines':    field2lines,
    'text':     field2text,
    'boolean':  field2boolean,
    }

get_converter = type_converters.get

def registerTypeConverter(field_type, converter, replace=False):
    """Add a custom type converter to the registry.

    If 'replace' is not true, raise a KeyError if a converter is
    already registered for 'field_type'.
    """
    existing = type_converters.get(field_type)

    if existing is not None and not replace:
        raise KeyError('Existing converter for field_type: %s' % field_type)

    type_converters[field_type] = converter

