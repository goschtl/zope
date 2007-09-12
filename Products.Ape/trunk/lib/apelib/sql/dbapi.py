##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""SQL database connections via DB-API 2.0.

$Id$
"""

import os
import re
from time import time

from apelib.core.interfaces import ITPCConnection
from apelib.core.schemas import ColumnSchema
from apelib.sql.interfaces import ISQLConnection, IRDBMSColumn
from apelib.sql.table import SQLTable

name_style_re = re.compile(':[A-Za-z0-9_-]+')

DEBUG = os.environ.get('APE_DEBUG_SQL')
PROFILE = os.environ.get('APE_PROFILE_SQL')


class AbstractSQLConnection:

    __implements__ = ISQLConnection, ITPCConnection

    # factories by column name take precedence over factories by column type.
    column_factories_by_name = {}  # { local col name -> column factory }
    column_factories_by_type = {}  # { local type name -> column factory }
    column_name_translations = {}  # { local col name -> db col name }
    column_type_translations = {}  # { local type name -> db type name }
    module = None
    connector = None

    def __init__(self, module_name, connect_expression, prefix=''):
        # connect_expression is a Python expression.
        self.module_name = module_name
        self.module = __import__(module_name, {}, {}, ('__doc__',))
        if not hasattr(self.module, "connect"):
            raise ImportError(
                "Module '%s' does not have a 'connect' method." % module_name)
        self.connect_expression = connect_expression
        self.prefix = prefix
        self.connector = None
        self.transaction_started = False
        self._tables = {}
        self._final = 0

    def __repr__(self):
        return '<%s(module_name=%s)>' % (
            self.__class__.__name__, repr(self.module_name))

    #
    # IRDBMSConnection implementation.
    #

    def define_table(self, name, schema):
        """Creates and returns an IRDBMSTable."""
        table = SQLTable(self, self.prefix + name)
        for c in schema.get_columns():
            factory = self.column_factories_by_name.get(c.name)
            if factory is None:
                factory = self.column_factories_by_type.get(c.type)
            if factory is None:
                factory = RDBMSColumn
            dbc = factory(self, c)
            n = self.column_name_translations.get(c.name)
            if n is not None:
                dbc.name = n
            t = self.column_type_translations.get(c.type)
            if t is not None:
                dbc.type = t
            table.add_column(c.name, dbc)
        self._tables[name] = table
        return table

    def get_table(self, name):
        """Returns a previously defined IRDBMSTable."""
        return self._tables[name]

    def exists(self, name, type_name):
        """Returns true if the specified database object exists.

        type_name is 'table' or 'sequence'
        """
        raise NotImplementedError("Abstract Method")

    def list_table_names(self):
        """Returns a list of existing table names.
        """
        raise NotImplementedError("Abstract Method")

    def create_sequence(self, name, start=1):
        """Creates a sequence.
        """
        raise NotImplementedError("Abstract Method")

    def reset_sequence(self, name, start=1):
        """Resets a sequence.
        """
        raise NotImplementedError("Abstract Method")

    def increment(self, name):
        """Increments a sequence.
        """
        raise NotImplementedError("Abstract Method")

    def clear_table(self, name):
        """Removes all rows from a table.
        """
        self.execute('DELETE FROM %s' % (self.prefix + name))

    def execute(self, sql, kw=None, fetch=False):
        if self.connector is None:
            raise RuntimeError('Not connected')
        converter = style_converters[self.module.paramstyle]
        sql, param_names = converter(sql)
        if param_names is None:
            # The query expects keyword parameters.
            params = kw or {}
        else:
            # The query expects positional parameters.
            if not param_names:
                params = ()
            else:
                params = tuple([kw[n] for n in param_names])
        self.transaction_started = True
        cursor = self.connector.cursor()
        try:
            if DEBUG or PROFILE:
                print 'SQL: %s, %s' % (repr(sql), params)
            if PROFILE:
                start = time()
                cursor.execute(sql, params)
                end = time()
                print 'SQL time: %0.6fs' % (end - start)
            else:
                if not params:
                    cursor.execute(sql)
                else:
                    cursor.execute(sql, params)
            if fetch:
                res = list(cursor.fetchall())
                if DEBUG:
                    print 'SQL result: %s' % repr(res)
                return res
        finally:
            cursor.close()

    #
    # ITPCConnection implementation.
    #

    def connect(self):
        d = {'connect': self.module.connect}
        self.connector = eval(self.connect_expression, d)

    def sortKey(self):
        return repr(self)

    def getName(self):
        return repr(self)

    def begin(self):
        pass

    def vote(self):
        self._final = 1

    def reset(self):
        self._final = 0
        self.transaction_started = False

    def abort(self):
        try:
            if DEBUG:
                print 'SQL ROLLBACK'
            self.connector.rollback()
        finally:
            self.reset()

    def finishWrite(self):
        pass

    def finishCommit(self):
        if self._final:
            try:
                if DEBUG:
                    print 'SQL COMMIT'
                self.connector.commit()
            finally:
                self.reset()

    def close(self):
        c = self.connector
        if c is not None:
            self.connector = None
            c.close()

# Converters for all parameter styles defined by DB-API 2.0.
# Each converter returns translated SQL and a list of positional parameters.
# The list of positional parameters may be None, indicating that a dictionary
# should be supplied rather than a tuple.

style_converters = {}

def convert_to_qmark(sql):
    # '?' format
    params = []
    def replace(match, params=params):
        name = match.group()[1:]
        params.append(name)
        return '?'
    sql = name_style_re.sub(replace, sql)
    return sql, params
style_converters['qmark'] = convert_to_qmark

def convert_to_numeric(sql):
    # ':1' format
    params = []
    def replace(match, params=params):
        name = match.group()[1:]
        index = len(params)
        params.append(name)
        return ':%d' % index
    sql = name_style_re.sub(replace, sql)
    return sql, params
style_converters['numeric'] = convert_to_numeric

def convert_to_named(sql):
    # ':name' format
    # The input format is the same as the output format.
    return sql, None
style_converters['named'] = convert_to_named

def convert_to_format(sql):
    # '%s' format
    params = []
    def replace(match, params=params):
        name = match.group()[1:]
        params.append(name)
        return '%s'
    sql = name_style_re.sub(replace, sql)
    return sql, params
style_converters['format'] = convert_to_format

def convert_to_pyformat(sql):
    # '%(name)s' format
    def replace(match):
        name = match.group()[1:]
        return '%%(%s)s' % name
    sql = name_style_re.sub(replace, sql)
    return sql, None
style_converters['pyformat'] = convert_to_pyformat



# RDBMS column implementations.

class RDBMSColumn(ColumnSchema):
    """Basic RDBMS column.  Does no type translation."""
    __implements__ = IRDBMSColumn

    use_conversion = False

    def __init__(self, connection, column):
        self.name = column.name
        self.type = column.type
        self.unique = column.unique

    def to_db(self, value):
        return value

    def from_db(self, value):
        return value


class IntColumn(RDBMSColumn):
    """RDBMS column that stores as integers."""
    __implements__ = IRDBMSColumn

    use_conversion = True

    def to_db(self, value):
        return int(value)

    def from_db(self, value):
        return str(value)


class LongColumn(RDBMSColumn):
    """RDBMS column that stores as long integers."""
    __implements__ = IRDBMSColumn

    use_conversion = True

    def to_db(self, value):
        return long(value)

    def from_db(self, value):
        return str(value)


class BlobColumn (RDBMSColumn):
    """RDBMS column that stores Binary objects."""
    __implements__ = IRDBMSColumn

    use_conversion = True

    def __init__(self, connection, column):
        RDBMSColumn.__init__(self, connection, column)
        self.Binary = connection.module.Binary

    def to_db(self, value):
        return self.Binary(value)

    def from_db(self, value):
        if hasattr(value, 'tostring'):
            # possibly an array (see Python's array module)
            return value.tostring()
        return str(value)


# Set up default column types.
AbstractSQLConnection.column_factories_by_name['oid'] = IntColumn
AbstractSQLConnection.column_factories_by_type['blob'] = BlobColumn
