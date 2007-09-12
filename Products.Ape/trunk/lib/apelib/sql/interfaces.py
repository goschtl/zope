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
"""Interfaces for apelib.sql.

$Id$
"""

from Interface import Interface
from Interface.Attribute import Attribute
from apelib.core.interfaces import IColumnSchema


class IRDBMSConnection (Interface):
    """Interface of basic RDBMS connections.

    This interface provides only relatively basic operations.  Create
    subinterfaces for complex and vendor-specific extensions.
    """

    module = Attribute("module", "The DB-API module")

    connector = Attribute("connector", "The shared DB-API connection")

    def define_table(name, schema):
        """Creates and returns an IRDBMSTable.

        Does not create the table in the database.  table.create()
        creates the table.
        """

    def get_table(name):
        """Returns a previously defined IRDBMSTable."""

    def exists(name, type_name):
        """Returns true if the specified database object exists.

        'name' is the name of the object.  'type_name' is 'table' or
        'sequence'.
        """

    def list_table_names():
        """Returns a list of existing table names."""

    def create_sequence(name, start=1):
        """Creates a sequence."""

    def reset_sequence(name, start=1):
        """Resets a sequence to a starting value."""

    def increment(name):
        """Increments a sequence and returns the value.

        Whether the value is before or after the increment is not specified.
        """

    def clear_table(name):
        """Removes all rows from a table.

        This is not a method of IRDBMSTable because it is not
        always possible to construct an IRDBMSTable while resetting
        tables.
        """


class ISQLConnection (IRDBMSConnection):

    def execute(sql, kw=None, fetch=False):
        """Executes a SQL query.

        If kw is provided, parameters in the SQL are substituted for
        parameter values.  If fetch is true, the rows from the results
        are returned.  No type conversion happens in execute().
        """


class IRDBMSTable (Interface):
    """A table in a database."""

    def select(result_col_names, **filter):
        """Selects rows from a table and returns column values for those rows.
        """

    def insert(col_names, row):
        """Inserts one row in the table."""

    def set_one(oid, col_names, row, is_new):
        """Sets one row in the table.

        Executes either an update or insert operation, depending
        on the is_new argument and configured policies.
        """

    def set_many(oid, key_col_names, other_col_names, rows):
        """Sets multiple rows in the table.

        'rows' is a sequence of tuples containing values for the
        key_col_names as well as the other_col_names.

        Either deletes all rows for an oid and inserts new rows, or
        examines the current state of the database and modifies it in
        pieces.
        """

    def delete_rows(**filter):
        """Deletes rows from the table."""

    def create():
        """Creates the table."""

    def drop():
        """Drops the table."""


class IRDBMSColumn (IColumnSchema):
    """A column associated with a specific database."""

    use_conversion = Attribute(
        "use_conversion", "True if this column needs to convert values.")

    def to_db(value):
        """Converts a generic value to a database-specific value."""

    def from_db(value):
        """Converts a database-specific value to a generic value."""

