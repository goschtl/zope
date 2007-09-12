##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Zope 2 script serialization

$Id$
"""

import re
from types import StringType

from Products.PythonScripts.PythonScript import PythonScript
from Products.ZSQLMethods.SQL import SQL, SQLConnectionIDs
from Shared.DC.ZRDB.Aqueduct import parse
try:
    from IOBTree import Bucket
except ImportError:
    Bucket = lambda: {}

from apelib.core.interfaces import ISerializer
from apelib.core.schemas import ColumnSchema, RowSequenceSchema


class PythonScriptSerializer:
    """Serializer for PythonScripts.

    PythonScriptSerializer serializes using the same representation
    as FTP or WebDAV.  All computable attributes like compiled code
    are dropped.
    """

    __implements__ = ISerializer

    schema = ColumnSchema('data', 'string')

    def can_serialize(self, obj):
        return isinstance(obj, PythonScript)

    def serialize(self, event):
        assert isinstance(event.obj, PythonScript)
        data = event.obj.read()
        assert isinstance(data, StringType)
        event.ignore((
            'title', '_params', '_body', '_bind_names',
            'warnings', 'errors', '_code', 'Python_magic', 
            'Script_magic', 'func_defaults', 'func_code', 
            'co_varnames', 'co_argcount',
            ))
        return data

    def deserialize(self, event, state):
        obj = event.obj
        assert isinstance(state, StringType)
        assert isinstance(event.obj, PythonScript)
        # Circumvent proxy role checking while deserializing the script.
        obj._validateProxy = lambda: 0
        try:
            obj.write(state) 
            obj._makeFunction()
        finally:
            # Remove the proxy circumvention
            del obj._validateProxy



class ZSQLMethodSerializer:
    """Serializer for ZSQLMethods.

    ZSQLMethodSerializer serializes using the same representation
    as FTP or WebDAV.  All computable attributes like compiled code
    are dropped.
    """

    __implements__ = ISerializer

    schema = ColumnSchema('data', 'string')

    params_re = re.compile(r'\s*<params>(.*)</params>\s*\n', re.I | re.S)

    def can_serialize(self, obj):
        return isinstance(obj, SQL)

    def serialize(self, event):
        data = event.obj.document_src()
        event.ignore(('_arg', 'template', 'arguments_src', 'src'))
        return data

    def deserialize(self, event, state):
        obj = event.obj
        assert isinstance(state, StringType)
        assert isinstance(obj, SQL)
        body = state
        m = self.params_re.match(body)
        if m:
            obj.arguments_src = m.group(1)
            body = body[m.end():]
        else:
            obj.arguments_src = ''
        obj._arg = parse(obj.arguments_src)
        obj.src = body
        obj.template = obj.template_class(body)
        obj.template.cook()
        obj._v_cache = ({}, Bucket())
        if not hasattr(obj, 'connection_id'):
            obj.connection_id = ''


class ZSQLMethodPropertiesSerializer:
    __implements__ = ISerializer

    schema = RowSequenceSchema()
    schema.add('id', 'string', 1)
    schema.add('type', 'string')
    schema.add('data', 'string')

    attributes = {
        'title': str,
        'connection_id': str,
        'max_rows_': int,
        'max_cache_': int,
        'cache_time': int, 
        'class_name_': str, 
        'class_file_': str,
        'zclass': str, # XXX, what's that 
        'allow_simple_one_argument_traversal': int,
        'connection_hook': str, 
    }

    def can_serialize(self, obj):
        return isinstance(obj, SQL)

    def serialize(self, event):
        obj = event.obj
        assert isinstance(obj, SQL)
        res = []
        for attribute, factory in self.attributes.items():
            if not hasattr(obj, attribute):
                continue
            value = getattr(obj, attribute)
            t = factory.__name__
            if value is None:
                if factory in (int, long):
                    value = 0
                else: 
                    value = ''
            value = str(value)
            event.serialized(attribute, value, 1)
            res.append((attribute, t, value))
        event.ignore('_col') 
        return res 

    def deserialize(self, event, state):
        obj = event.obj
        assert isinstance(obj, SQL)
        for attribute, t, value in state:
            factory = self.attributes.get(attribute)
            if factory is None:
                continue
            value = factory(value)
            setattr(obj, attribute, value)
            event.deserialized(attribute, value)
        if not hasattr(obj, 'connection_id'):
            obj.connection_id = ''

