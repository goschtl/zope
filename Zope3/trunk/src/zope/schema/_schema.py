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
$Id: _schema.py,v 1.4 2003/01/25 05:13:48 rdmurray Exp $
"""
from zope.interface import Interface
from zope.schema.interfaces import ValidationError

def getFields(schema):
    """Get all fields on a schema.
    """
    from zope.schema.interfaces import IField
    fields = {}
    for name in schema.names(all=True):
        attr = schema.getDescriptionFor(name)
        if IField.isImplementedBy(attr):
            fields[name] = attr
    return fields

def getFieldsInOrder(schema,
                     _fieldsorter=lambda x, y: cmp(x[1].order, y[1].order)):
    """Get a list of (name, value) tuples in native schema order.
    """
    fields = getFields(schema).items()
    fields.sort(_fieldsorter)
    return fields
