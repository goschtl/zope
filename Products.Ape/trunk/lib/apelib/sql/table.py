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
"""SQL implementation of IRDBMSTable.

$Id$
"""

from apelib.sql.interfaces import IRDBMSTable, IRDBMSColumn


class SQLTable:
    """Talks to a table via SQL."""

    __implements__ = IRDBMSTable

    def __init__(self, connection, name):
        self.name = name
        self.execute = connection.execute
        self.columns = {}
        self.column_order = []

    def add_column(self, name, column):
        assert not self.columns.has_key(name)
        assert IRDBMSColumn.isImplementedBy(column)
        self.columns[name] = column
        self.column_order.append(name)

    def cache(self, m, *params):
        # In the future, this will integrate with AbstractSQLConnection
        # to provide a clean way to cache and prepare database queries.
        return m(*params)

    def generate_conditions(self, col_names):
        clauses = [
            "%s = :%s" % (self.columns[c].name, c) for c in col_names]
        return ' AND '.join(clauses)

    def generate_select(self, filter_col_names, result_col_names):
        result_names = [self.columns[col].name for col in result_col_names]
        sql = 'SELECT %s FROM %s' % (', '.join(result_names), self.name)
        where = self.generate_conditions(filter_col_names)
        if where:
            sql += ' WHERE %s' % where
        return sql

    def generate_insert(self, col_names):
        db_names = [self.columns[c].name for c in col_names]
        colfmts = [':%s' % c for c in col_names]
        return 'INSERT INTO %s (%s) VALUES (%s)' % (
            self.name, ', '.join(db_names), ', '.join(colfmts))

    def generate_update(self, key_col_names, other_col_names):
        where = self.generate_conditions(key_col_names)
        to_set = [
            ("%s = :%s" % (self.columns[c].name, c))
            for c in other_col_names]
        return 'UPDATE %s SET %s WHERE %s' % (
            self.name, ', '.join(to_set), where)

    def generate_delete(self, col_names):
        where = self.generate_conditions(col_names)
        sql = 'DELETE FROM %s' % self.name
        if where:
            sql += ' WHERE %s' % where
        return sql

    def prepare_for_db(self, col_names, data, oid=None):
        """Prepares one row for writing to the database."""
        res = {}
        for n in range(len(col_names)):
            c = col_names[n]
            res[c] = self.columns[c].to_db(data[n])
        if oid is not None:
            res['oid'] = self.columns['oid'].to_db(oid)
        return res

    #
    # IRDBMSTable implementation.
    #

    def select(self, result_col_names, **filter):
        """Selects rows from a table and returns column values for those rows.
        """
        f = {}
        for col_name, value in filter.items():
            f[col_name] = self.columns[col_name].to_db(value)
        sql = self.cache(self.generate_select, filter.keys(), result_col_names)
        db_res = self.execute(sql, f, fetch=1)
        # Convert the results to standard types.
        conversions = []
        for n in range(len(result_col_names)):
            col = self.columns[result_col_names[n]]
            if col.use_conversion:
                conversions.append((n, col.from_db))
        if conversions:
            # Convert specific columns.
            res = []
            for row in db_res:
                r = list(row)
                for n, from_db in conversions:
                    r[n] = from_db(r[n])
                res.append(tuple(r))
        else:
            # No conversion needed.
            res = db_res
        return res

    def insert(self, col_names, row):
        """Inserts one row in the table.
        """
        kw = self.prepare_for_db(col_names, row)
        sql = self.cache(self.generate_insert, col_names)
        self.execute(sql, kw)

    def set_one(self, oid, col_names, row, is_new):
        """Sets one row in a table.

        Requires the table to have only one value for each oid.
        Executes either an update or insert operation, depending on
        the is_new argument and configured policies.
        """
        kw = self.prepare_for_db(col_names, row, oid)
        if is_new:
            sql = self.cache(self.generate_insert, ('oid',) + tuple(col_names))
            self.execute(sql, kw)
        else:
            sql = self.cache(self.generate_update, ('oid',), col_names)
            self.execute(sql, kw)

    def set_many(self, oid, key_col_names, other_col_names, rows):
        """Sets multiple rows in a table.

        'rows' is a sequence of tuples containing values for the
        key_columns as well as the other_columns.

        Either deletes all rows for an oid and inserts new rows, or
        examines the current state of the database and modifies it in
        pieces.
        """
        combo = tuple(key_col_names) + tuple(other_col_names)
        if not key_col_names:
            # Don't compare rows.  Just delete and insert.
            kw = self.prepare_for_db((), (), oid)
            sql = self.cache(self.generate_delete, ('oid',))
            self.execute(sql, kw)
            sql = self.cache(self.generate_insert, ('oid',) + combo)
            for row in rows:
                kw = self.prepare_for_db(combo, row, oid)
                self.execute(sql, kw)
            return
        # Edit the table.
        exist_rows = self.select(combo, oid=oid)
        count = len(key_col_names)
        existing = {}
        for record in exist_rows:
            key = tuple(record[:count])
            value = tuple(record[count:])
            existing[key] = value
        now = {}
        for record in rows:
            key = tuple(record[:count])
            value = tuple(record[count:])
            now[key] = value
        # Delete and update rows.
        for key, value in existing.items():
            if not now.has_key(key):
                # Delete this row.
                kw = self.prepare_for_db(key_col_names, key, oid)
                sql = self.cache(
                    self.generate_delete, ('oid',) + tuple(key_col_names))
                self.execute(sql, kw)
            elif now[key] != value:
                # Update this row.
                #print 'DIFFERENT:', now[key], value
                kw = self.prepare_for_db(combo, key + now[key], oid)
                cols = ('oid',) + tuple(key_col_names)
                sql = self.cache(self.generate_update, cols, other_col_names)
                self.execute(sql, kw)
        for key, value in now.items():
            if not existing.has_key(key):
                # Insert this row.
                kw = self.prepare_for_db(combo, key + value, oid)
                sql = self.cache(self.generate_insert, ('oid',) + combo)
                self.execute(sql, kw)
        return

    def delete_rows(self, **filter):
        """Deletes rows from the table.
        """
        sql = self.cache(self.generate_delete, filter.keys())
        self.execute(sql, filter)

    def create(self):
        """Creates the table.
        """
        pkeys = []
        col_decls = []
        for c in self.column_order:
            col = self.columns[c]
            constraints = ''
            if col.unique:
                constraints = ' NOT NULL'
                pkeys.append(col.name)
            col_decls.append(
                "%s %s%s" % (col.name, col.type, constraints))
        if pkeys:
            col_decls.append('PRIMARY KEY (%s)' % ', '.join(pkeys))
        sql = "CREATE TABLE %s (%s)" % (self.name, ', '.join(col_decls))
        self.execute(sql)

    def drop(self):
        """Drops the table.
        """
        sql = "DROP TABLE %s" % self.name
        self.execute(sql)
