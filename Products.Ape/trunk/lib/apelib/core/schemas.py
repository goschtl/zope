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
"""Basic schema implementations.

$Id$
"""

from types import StringType

from interfaces import IColumnSchema

ok_types = [
    'unicode', 'string', 'int', 'long', 'float', 'bool', 'boolean', 'text',
    'object', 'classification', 'string:list', 'blob',
    ]


def add_column_type(t):
    """Adds an allowable column type."""
    assert isinstance(t, StringType)
    if t not in ok_types:
        ok_types.append(t)


class ColumnSchema:
    """Defines the schema of one column."""

    __implements__ = IColumnSchema
    name = None
    type = None
    unique = None

    def __init__(self, name, type='string', unique=0):
        assert type in ok_types, type
        self.name = name
        self.type = type
        self.unique = not not unique

    def get_columns(self):
        return [self]

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (other.name == self.name) and (other.type == self.type) and (
                other.unique == self.unique):
                return 1  # Same
        return 0  # Different

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'ColumnSchema(%s, %s, %s)' % (
            repr(self.name), repr(self.type), repr(self.unique))

# b/w compat.
FieldSchema = ColumnSchema


class RowSequenceSchema:
    """Defines a schema for a sequence of rows, including row count limits.
    """
    def __init__(self, columns=(), min_rows=0, max_rows=0):
        # max_rows == 0 means unlimited.
        assert (max_rows == 0 or max_rows >= min_rows)
        self.min_rows = min_rows
        self.max_rows = max_rows
        self.columns = []
        self.column_names = {}
        for c in columns:
            self._add(c)

    def get_columns(self):
        res = []
        for f in self.columns:
            res.extend(f.get_columns())
        return res

    def _add(self, c):
        if self.column_names.has_key(c.name):
            raise KeyError, 'Duplicate column name: %s' % c.name
        self.column_names[c.name] = 1
        self.columns.append(c)

    def add(self, name, type='string', unique=0):
        self._add(ColumnSchema(name, type, unique))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (self.columns == other.columns) and (
                self.min_rows == other.min_rows) and (
                self.max_rows == other.max_rows):
                return 1  # Same
        return 0  # Different

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return 'RowSequenceSchema(%s, min_rows=%s, max_rows=%s)' % (
            repr(self.columns), repr(self.min_rows), repr(self.max_rows))
