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
"""PostgreSQL-specific database connection.

$Id$
"""

from apelib.sql.dbapi import AbstractSQLConnection


class PostgreSQLConnection (AbstractSQLConnection):

    column_type_translations = {
        'long':   'bigint',
        'string': 'character varying(255)',
        'blob':   'bytea',
        'datetime': 'timestamp',
        }

    column_name_translations = {
        'oid': 'objoid',
        }

    def exists(self, name, type_name):
        """Returns true if the specified database object exists.

        type_name is 'table' or 'sequence'
        """
        table_name = self.prefix + name
        if type_name == 'table':
            sql = ('SELECT tablename FROM pg_tables '
                   'WHERE tablename = :name')
        elif type_name == 'sequence':
            sql = ("SELECT relname FROM pg_class "
                   "WHERE relkind = 'S' AND relname = :name")
        else:
            raise ValueError(type_name)
        rows = self.execute(sql, {'name': table_name.lower()}, fetch=1)
        return len(rows)

    def list_table_names(self):
        """Returns a list of existing table names.
        """
        sql = 'SELECT tablename FROM pg_tables'
        rows = self.execute(sql, {}, fetch=1)
        res = []
        for (name,) in rows:
            if not self.prefix or name.startswith(self.prefix):
                res.append(name[len(self.prefix):])
        return res

    def create_sequence(self, name, start=1):
        """Creates a sequence.
        """
        sql = "CREATE SEQUENCE %s START %d" % (self.prefix + name, start)
        self.execute(sql)

    def reset_sequence(self, name, start=1):
        """Resets a sequence.
        """
        sql = "SELECT setval('%s', %d)" % (self.prefix + name, start)
        self.execute(sql)

    def increment(self, name):
        """Increments a sequence.
        """
        sql = "SELECT nextval('%s')" % (self.prefix + name)
        rows = self.execute(sql, fetch=1)
        return rows[0][0]
