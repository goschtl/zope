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
"""MySQL-specific database connection.

$Id$
"""

from apelib.sql.dbapi import AbstractSQLConnection

class MySQLConnection (AbstractSQLConnection):

    column_type_translations = {
        'long':   'bigint',
        'string': 'character varying(255)',
        'blob':   'longblob',
        'boolean': 'tinyint(1)',
        }

    column_name_translations = {
        'oid': 'objoid',
        }

    def exists(self, name, type_name):
        """Returns true if the specified database object exists.

        type_name is 'table' or 'sequence'
        """
        table_name = self.prefix + name
        if type_name not in ('table', 'sequence'):
            raise ValueError(type_name)
        sql = 'SHOW TABLES LIKE :name'
        rows = self.execute(sql, {'name': table_name}, fetch=1)
        return len(rows)

    def list_table_names(self):
        """Returns a list of existing table names.
        """
        sql = 'SHOW TABLES'
        rows = self.execute(sql, {}, fetch=1)
        res = []
        for (name,) in rows:
            if not self.prefix or name.startswith(self.prefix):
                res.append(name[len(self.prefix):])
        return res

    def create_sequence(self, name, start=1):
        """Creates a sequence.
        """
        table_name = self.prefix + name
        self.execute("CREATE TABLE %s (last_value int)" % table_name)
        self.execute("INSERT INTO %s VALUES (%d)" % (table_name, start))

    def reset_sequence(self, name, start=1):
        """Resets a sequence.
        """
        table_name = self.prefix + name
        self.execute("UPDATE %s SET last_value=0" % table_name)

    def increment(self, name):
        """Increments a sequence.
        """
        table_name = self.prefix + name
        self.execute(
            "UPDATE %s SET last_value=LAST_INSERT_ID(last_value+1)" %
            table_name)
        rows = self.execute("SELECT LAST_INSERT_ID()", fetch=1)
        return rows[0][0]

