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
"""ZODB tables with support for basic relational operations.

$Id$
"""

import ZODB
from Persistence import Persistent
from BTrees.IIBTree import IITreeSet, intersection
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from BTrees.OOBTree import OOBTree
from Record import Record


class DuplicateError(Exception):
    """Duplicated data record"""


class Column:

    def __init__(self, name, primary, indexed):
        self.name = name        # string
        self.primary = primary  # boolean
        self.indexed = indexed  # boolean

    def __repr__(self):
        return "<%s(%s)>" % (self.__class__.__name__, self.name)


class TableSchema:

    reserved_names = ('rid',)

    def __init__(self):
        self.columns = []
        self.column_names = {}

    def add(self, name, primary=0, indexed=0):
        if name in self.reserved_names:
            raise ValueError, "Column name %s is reserved" % repr(name)
        if self.column_names.has_key(name):
            raise ValueError, "Column %s already exists" % repr(name)
        self.column_names[name] = 1
        self.columns.append(Column(name, primary, indexed))

    def get_columns(self):
        return tuple(self.columns)

    def __repr__(self):
        names = []
        for c in self.columns:
            names.append(c.name)
        return "<%s(%s)>" % (self.__class__.__name__, ', '.join(names))


class TableRecordMixin:

    def __repr__(self):
        items = []
        for name, position in self.__record_schema__.items():
            value = repr(getattr(self, name))
            items.append((position, "%s=%s" % (name, value)))
        items.sort()
        params = []
        for position, p in items:
            params.append(p)
        return "<%s(%s)>" % (self.__class__.__name__, ', '.join(params))


class Table(Persistent):
    """Simple, generic relational table.
    """
    schema = None
    _v_record_class = None

    def __init__(self, schema=None):
        if schema is not None:
            self.schema = schema
        columns = schema.get_columns()
        self.col_info = []  # [(tuple position, column),]
        self.positions = {}
        for i in range(len(columns)):
            # Leave space for the record ID at position 0.
            position = i + 1
            self.col_info.append((position, columns[i]))
            self.positions[columns[i].name] = position
        self.proto_record = [None] * (len(columns) + 1)
        self.next_rid = 1
        self.clear()


    def clear(self):
        self.data = IOBTree()  # {rid -> record as tuple}
        self.indexes = {}      # {index_name -> OOBTree({value -> IITreeSet})}
        self.primary_index = OIBTree()  # {primary key -> rid}
        for position, column in self.col_info:
            if column.indexed:
                self.indexes[column.name] = OOBTree()


    def tuplify(self, params):
        """Accepts a mapping-like object and returns a tuple.
        """
        record = self.proto_record[:]
        positions = self.positions
        if hasattr(params, '__record_schema__'):
            for name in params.__record_schema__.keys():
                position = positions[name]
                record[position] = params[name]
        else:
            for name, value in params.items():
                position = positions[name]
                record[position] = value
        return tuple(record)


    def insert(self, params):
        record = self.tuplify(params)

        # Determine the primary key.
        primary_key = []
        for position, column in self.col_info:
            if column.primary:
                if record[position] is None:
                    raise ValueError, (
                        "No value provided for primary key column %s"
                        % repr(column.name))
                primary_key.append(record[position])
        if primary_key:
            primary_key = tuple(primary_key)
            if self.primary_index.has_key(primary_key):
                raise DuplicateError(
                    "Primary key %s in use" % repr(primary_key))

        # Add a record.
        rid = self.next_rid
        self.next_rid += 1   # XXX Hotspot!
        record = (rid,) + record[1:]
        self.data[rid] = record
        if primary_key:
            self.primary_index[primary_key] = rid

        # Add to indexes.
        for position, column in self.col_info:
            name = column.name
            value = record[position]
            if value is not None:
                if self.indexes.has_key(name):
                    set = self.indexes[name].get(value)
                    if set is None:
                        set = IITreeSet()
                        self.indexes[name][value] = set
                    set.insert(rid)

        # Return the number of rows inserted.
        return 1


    def delete(self, filter):
        rids = self._select_rids(self.tuplify(filter))
        if rids is None:
            # Zap everything
            count = len(self.data)
            self.clear()
            return count
        elif not rids:
            # No rows selected
            return 0

        rids = tuple(rids)  # Make sure rids is a static sequence
        for rid in rids:
            old_r = self.data[rid]
            assert old_r[0] == rid
            primary_key = []
            for position, column in self.col_info:
                old_value = old_r[position]
                if old_value is not None:
                    if column.primary:
                        primary_key.append(old_value)
                    # Remove from indexes.
                    index = self.indexes.get(column.name)
                    if index is not None:
                        if index.has_key(old_value):
                            # Remove an index entry.
                            set = index[old_value]
                            set.remove(rid)
                            if not set:
                                del index[old_value]

            if primary_key:
                # Remove a primary key.
                primary_key = tuple(primary_key)
                assert self.primary_index[primary_key] == rid
                del self.primary_index[primary_key]

            # Remove the data.
            del self.data[rid]

        return len(rids)


    def update(self, filter, changes):
        rids = self._select_rids(self.tuplify(filter))
        if rids is None:
            rids = self.data.keys()
        elif not rids:
            # Nothing needs to be updated.
            return 0
        count = len(rids)

        # Identify changes.
        old_data = {}    # rid -> old tuple
        new_data = {}    # rid -> new tuple
        old_to_new = {}  # old primary key -> new primary key
        new_to_rid = {}  # new primary key -> rid

        record = self.tuplify(changes)
        for rid in rids:
            old_r = self.data[rid]
            old_data[rid] = old_r
            new_r = list(old_r)
            # new_r and old_r contain record tuples.
            for position, column in self.col_info:
                if record[position] is not None:
                    new_r[position] = record[position]
            new_data[rid] = tuple(new_r)
            # Hmm.  The code below allows an update to change the primary
            # key.  It might be better to prevent primary key columns from
            # being changed by an update() call.
            opk = []
            npk = []
            for position, column in self.col_info:
                if column.primary:
                    opk.append(old_r[position])
                    npk.append(new_r[position])
            if opk != npk:
                opk = tuple(opk)
                npk = tuple(npk)
                old_to_new[opk] = npk
                new_to_rid[npk] = rid

        # Look for primary key conflicts.  A primary key conflict can
        # occur when changing a record to a different primary key and
        # the new primary key is already in use.
        for pk in old_to_new.values():
            if (self.primary_index.has_key(pk)
                and not old_to_new.has_key(pk)):
                raise DuplicateError("Primary key %s in use" % repr(pk))

        # Update the data.
        self.data.update(new_data)

        # Remove old primary key indexes and insert new primary key indexes.
        for pk in old_to_new.keys():
            del self.primary_index[pk]
        self.primary_index.update(new_to_rid)

        # Update indexes.
        for rid, old_r in old_data.items():
            for position, column in self.col_info:
                index = self.indexes.get(column.name)
                if index is not None:
                    new_value = record[position]
                    old_value = old_r[position]
                    if new_value != old_value:
                        if old_value is not None and index.has_key(old_value):
                            # Remove an index entry.
                            set = index[old_value]
                            set.remove(rid)
                            if not set:
                                del index[old_value]
                        if new_value is not None:
                            # Add an index entry.
                            set = index.get(new_value)
                            if set is None:
                                set = IITreeSet()
                                index[new_value] = set
                            set.insert(rid)

        # Return the number of rows affected.
        return count


    def get_record_class(self):
        klass = self._v_record_class
        if klass is None:
            schema = {'rid': 0}
            for position, column in self.col_info:
                schema[column.name] = position
            class TableRecord(TableRecordMixin, Record):
                __record_schema__ = schema
            self._v_record_class = klass = TableRecord
        return klass


    def select(self, filter):
        rids = self._select_rids(self.tuplify(filter))
        if rids is None:
            # All
            klass = self.get_record_class()
            return [klass(rec) for rec in self.data.values()]
        elif rids:
            # Some
            klass = self.get_record_class()
            data = self.data
            return [klass(data[rid]) for rid in rids]
        else:
            # None
            return []


    def _select_rids(self, query):
        """Searches the table for matches, returning record ids.

        Returns a sequence of record ids, or None for all records.
        """
        primary_key = []
        params = 0  # The number of parameters specified
        primary_params = 0  # The number of primary params specified
        for position, column in self.col_info:
            value = query[position]
            if value is not None:
                params += 1
                if column.primary:
                    primary_params += 1
                    if primary_key is not None:
                        primary_key.append(value)
            elif column.primary:
                # Didn't fully specify the primary key.
                # Can't search by primary key.
                primary_key = None

        if not params:
            # No query.  Select all.
            return None

        # First strategy: try to satisfy the request by consulting
        # the primary key index.
        if primary_key:
            # The primary key is complete.  The result set will have
            # either zero rows or one row.
            primary_key = tuple(primary_key)
            rid = self.primary_index.get(primary_key)
            if rid is None:
                return ()
            # Possibly filter out the single item.
            if params > primary_params:
                cand = self.data[rid]
                for position, column in self.col_info:
                    if query[position] is not None:
                        if cand[position] != query[position]:
                            # Not a match.
                            return ()
            return (rid,)

        # Second strategy: try to satisfy the request by intersecting
        # indexes.
        rids = None
        iteration_filters = []
        for position, column in self.col_info:
            value = query[position]
            if value is not None:
                index = self.indexes.get(column.name)
                if index is None:
                    iteration_filters.append((position, value))
                else:
                    set = index.get(value)
                    if set is None:
                        # No rows satisfy this criterion.
                        return ()
                    if rids is None:
                        rids = set
                    else:
                        rids = intersection(rids, set)
                    if not rids:
                        # No rows satisfy all criteria.
                        return ()
        if rids is not None:
            rids = rids.keys()

        if not iteration_filters:
            # Indexes did all the work.  No need to search each record.
            return rids

        # Fallback strategy: Eliminate items one by one.
        if rids is None:
            # Use the whole data set.
            candidates = self.data.values()
        else:
            # Use the specified records.
            candidates = [self.data[rid] for rid in rids]

        rids = []
        append = rids.append
        for cand in candidates:
            for position, value in iteration_filters:
                if cand[position] != value:
                    # Not a match.
                    break
            else:
                # A match.
                append(cand[0])
        return rids

    def __repr__(self):
        return "<%s(schema=%s)>" % (self.__class__.__name__, repr(self.schema))
