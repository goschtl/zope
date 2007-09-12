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
"""Ingres-specific database connection.

$Id$
"""

from apelib.sql import dbapi

class IngresConnection (dbapi.AbstractSQLConnection):
    """
    Name :  IngresConnection - class for Ingres

    Description
        sub-classing of all methods needed to support the Ingres
        relational database management system.

    Inputs  :

    Output  :

    Exceptions :

    History:
    1-Jul-2004 - (emma.mcgrattan@ca.com)
        created
    14-Jul-2004 - (grant.croker@ca.com)
        modified IngresConnection.exists() to work with
        paramstyle=qmark
    14-Jul-2004 - (grant.croker@ca.com)
        subclassed create_table into IngresConnection to make use
        of Performance features of Ingres.
    15-Jul-2004 - (grant.croker@ca.com)
        Corrected Syntax of "MODIFY TABLE ... "
        Corrected parameter passing (Changed '?' to 'table_name')
    18-Jul-2004 - (srisu02@ca.com)
        Corrected Syntax for sequence increments
    18-Jul-2004 - (srisu02@ca.com)
        Corrected Syntax for sequence fetch() i.e added fetch=1 as a parameter
        22-Jul-2004 - (srisu02@ca.com)
            Integrated changes from dbapi.py
            Made change for cache size while creating sequences
    """

    column_type_translations = {
        'long':   'bigint',
        'string': 'varchar(255)',
        'datetime': 'time',
        'boolean': 'tinyint',
        }

    column_name_translations = {
        'oid': 'objoid',
        }

    column_factories_by_name = (
        dbapi.AbstractSQLConnection.column_factories_by_name.copy())

    column_factories_by_type = (
        dbapi.AbstractSQLConnection.column_factories_by_type.copy())

    def exists(self, name, type_name):
        """Returns true if the specified database object exists.

        type_name is 'table' or 'sequence'
        """
        table_name = self.prefix + name
        if type_name == 'table':
            sql = ('SELECT table_name FROM iitables '
                   'WHERE table_name = :name')
        elif type_name == 'sequence':
            sql = ("SELECT seq_name FROM iisequences "
                   "WHERE seq_name = :name")
        else:
            raise ValueError(type_name)
        rows = self.execute(sql, {'name': table_name.lower()}, fetch=1)
        return len(rows)

    def list_table_names(self):
        """Returns a list of existing table names.
        """
        sql = 'SELECT table_name FROM iitables'
        rows = self.execute(sql, {}, fetch=1)
        res = []
        for (name,) in rows:
            if not self.prefix or name.startswith(self.prefix):
                res.append(name[len(self.prefix):])
        return res

    def create_sequence(self, name, start=1):
        """Creates a sequence.
        """
        sql = "CREATE SEQUENCE %s START WITH %d CACHE 500" % (
            self.prefix + name, start)
        self.execute(sql)

    def reset_sequence(self, name, start=1):
        """Resets a sequence.
        """
        sql = "ALTER SEQUENCE %s RESTART WITH %d" % (
            self.prefix + name, start)
        self.execute(sql)

    def increment(self, name):
        """Increments a sequence.
        """
        sql = "SELECT NEXT VALUE FOR %s" % (self.prefix + name)
        rows = self.execute(sql, fetch=1)
        return rows[0][0]

    def create_table(self, table, column_defs):
        """
        Name :  IngresConnection - class for Ingres

        Description
            sub-classing of all methods needed to support the Ingres
            relational database management system.

        Inputs  :

        Output  :

        Exceptions :

        History:
            14-Jul-2004 - (grant.croker@ca.com)
                Created - based on AbstractSQLConnection

            NOTES
            -----
            Ingres supports 4 table structures. Depending on the key
            some are more preferrable than others. HEAP and ISAM are
            being ruled out on performance and maintenance grounds.
            BTREE is normally the best catch all solution but
            suffers when the key is sequentially increasing. HASH is good
            for one hit lookups but can require a more-frequent maintenance
            routine.

            The page size of the tables created is controlled by the
            ingres_page_size variable. Valid values are: 2048, 4096,
            8192, 16384, 32768 and 65536.
            """
        ingres_page_size = 8192
        ingres_table_structure = "BTREE"
        table_name = self.prefix + table
        cols = []
        indexes = []
        for name, typ, unique in column_defs:
            col = self.translate_name(name)
            db_type = self.translate_type(typ)
            constraints = ''
            if unique:
                constraints = ' NOT NULL'
                indexes.append(col)
            cols.append("%s %s%s" % (col, db_type, constraints))
        sql = "CREATE TABLE %s (%s)" % (table_name, ', '.join(cols))
        self.execute(sql)
        if indexes:
            sql = "MODIFY %s TO %s UNIQUE ON %s WITH PAGE_SIZE=%d" % (
                table_name, ingres_table_structure, ', '.join(indexes),
                ingres_page_size)
            self.execute(sql)
        else:
            sql = "MODIFY %s TO %s WITH PAGE_SIZE=%d" % (
                table_name, ingres_table_structure, ingres_page_size)
            traceback.print_stack()
            self.execute(sql)

IngresConnection.column_factories_by_type['boolean'] = dbapi.IntColumn
IngresConnection.column_factories_by_type['int'] = dbapi.IntColumn
IngresConnection.column_factories_by_type['long'] = dbapi.LongColumn
