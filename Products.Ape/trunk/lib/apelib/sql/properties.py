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
"""SQL properties

$Id$
"""

from apelib.core.schemas import RowSequenceSchema
from apelib.core.interfaces import IGateway, IDatabaseInitializer
from sqlbase import SQLGatewayBase


# safe_property_types lists the property types that are safe to store
# in table columns.  Floats are not permitted because their value can
# change when converting to/from strings.  Dates (based on Zope's
# DateTime class) are not permitted because their precision is not
# well defined, some databases don't store time zones, and Zope's
# DateTime class is hard to convert to other date/time types without
# losing information.

safe_property_types = {
    'string': 1,
    'int': 1,
    'long': 1,
    'text': 1,
    'boolean': 1,
    }


class SQLProperties (SQLGatewayBase):
    """SQL properties gateway
    """

    __implements__ = SQLGatewayBase.__implements__

    schema = RowSequenceSchema()
    schema.add('id', 'string', 1)
    schema.add('type', 'string')
    schema.add('data', 'string')
    table_name = 'properties'
    table_schema = RowSequenceSchema()
    table_schema.add('id', 'string', 1)
    table_schema.add('type', 'string', 0)
    table_schema.add('data', 'blob', 0)

    def load(self, event):
        table = self.get_table(event)
        rows = table.select(self.column_names, oid=event.oid)
        rows.sort()
        return rows, tuple(rows)

    def store(self, event, state):
        table = self.get_table(event)
        rows = [(id, t, data) for id, t, data in state]
        table.set_many(event.oid, ('id',), ('type', 'data'), rows)
        state = list(state)
        state.sort()
        return tuple(state)


class SQLFixedProperties (SQLGatewayBase):
    """SQL fixed-schema properties gateway.
    """

    def __init__(self, conn_name, table_name, schema):
        self.table_name = table_name
        self.schema = schema
        SQLGatewayBase.__init__(self, conn_name)
        self.columns = schema.get_columns()

    def init(self, event):
        conn = self.get_connection(event)
        all = RowSequenceSchema(
            self.oid_columns + self.table_schema.get_columns())
        table = conn.define_table(self.table_name, all)
        if not conn.exists(self.table_name, 'table'):
            table.create()

    def load(self, event):
        table = self.get_table(event)
        recs = table.select(self.column_names, oid=event.oid)
        if not recs:
            return (), ()
        if len(recs) > 1:
            raise ValueError("Multiple records where only one expected")
        record = [str(value) for value in recs[0]]
        items = []
        cols = self.columns
        for n in range(len(cols)):
            name = cols[n].name
            if name.startswith('_'):
                prop_name = name[1:]
            else:
                prop_name = name
            items.append((prop_name, cols[n].type, record[n]))
        return items, tuple(record)

    def store(self, event, state, leftover=None):
        cols = self.columns
        statedict = {}  # prop name -> (type, value)
        for name, typ, value in state:
            statedict[name] = (typ, value)
        record = []
        for col in cols:
            name = col.name
            if name.startswith('_'):
                prop_name = name[1:]
            else:
                prop_name = name
            if statedict.has_key(prop_name):
                typ, value = statedict[prop_name]
                record.append(str(value))
                del statedict[prop_name]
            else:
                record.append(None)  # Hopefully this translates to null.
        if statedict:
            if leftover is not None:
                # Pass back a dictionary of properties not stored yet.
                leftover.update(statedict)
            else:
                raise ValueError(
                    "Extra properties provided for fixed schema: %s"
                    % statedict.keys())
        table = self.get_table(event)
        table.set_one(event.oid, self.column_names, record, event.is_new)
        return tuple(record)



class SQLMultiTableProperties (SQLGatewayBase):
    """Combines fixed and variable properties.
    """

    __implements__ = IGateway, IDatabaseInitializer

    schema = SQLProperties.schema

    table_name = 'property_tables'
    table_schema = RowSequenceSchema()
    table_schema.add('class_name', 'string', 1)
    table_schema.add('table_name', 'string', 0)
    oid_columns = []  # No OID column

    def __init__(self, conn_name='db'):
        self.var_props = SQLProperties(conn_name=conn_name)
        self.fixed_props = {}  # class name -> SQLFixedProperties instance
        SQLGatewayBase.__init__(self, conn_name)

    def get_sources(self, event):
        return None

    def init(self, event):
        conn = self.get_connection(event)
        table = conn.define_table(self.table_name, self.table_schema)
        if not conn.exists(self.table_name, 'table'):
            table.create()
        self.var_props.init(event)
        if event.clear_all:
            # Clear the fixed property tables.
            recs = table.select(('table_name',))
            for (name,) in recs:
                conn.clear_table(name)
            self.fixed_props = {}


    def get_schema_for_class(self, module_name, class_name):
        """Returns the class-defined property schema.

        This Zope2-ism should be made pluggable later on.
        """
        d = {}
        m = __import__(module_name, d, d, ('__doc__',))
        klass = getattr(m, class_name)
        schema = RowSequenceSchema()
        props = getattr(klass, '_properties', ())
        if not props:
            return None
        for p in props:
            if not safe_property_types.has_key(p['type']):
                # Don't store this property in its own column.
                # It is of a type that's hard to convert faithfully.
                continue
            prop_name = p['id']
            if prop_name == 'oid':
                name = '_oid'
            else:
                name = prop_name
            schema.add(name, p['type'], 0)
        return schema


    def get_fixed_props(self, event):
        """Returns a SQLFixedProperties instance or None.
        """
        classification = event.classification
        if classification is None:
            return None
        cn = classification.get('class_name')
        if cn is None:
            return None
        if self.fixed_props.has_key(cn):
            return self.fixed_props[cn]  # May be None

        # Gather info about the class
        pos = cn.rfind('.')
        if pos < 0:
            raise ValueError, "Not a qualified class name: %s" % repr(cn)
        module_name = cn[:pos]
        class_name = cn[pos + 1:]
        schema = self.get_schema_for_class(module_name, class_name)
        if schema is None or not schema.get_columns():
            # No fixed properties exist for this class.
            self.fixed_props[cn] = None
            return None

        # Allocate a table name
        conn = self.get_connection(event)
        table = self.get_table(event)
        rows = table.select(('table_name',), class_name=cn)
        if rows:
            table_name = rows[0][0]
        else:
            attempt = 0
            while 1:
                # Find an available table name.
                table_name = '%s_properties' % (class_name[:16])
                if attempt:
                    table_name += '_%02d' % attempt
                if not conn.exists(table_name, 'table'):
                    break
                attempt += 1
            table.insert(('class_name', 'table_name'), (cn, table_name))

        # Create the fixed properties and table
        fp = SQLFixedProperties(self.conn_name, table_name, schema)
        fp.init(event)
        # XXX If the transaction gets aborted, the table creation will
        # be undone, but self.fixed_props won't see the change.
        # Perhaps we need to reset self.fixed_props on abort.
        self.fixed_props[cn] = fp
        return fp


    def load(self, event):
        """Returns a combination of states from two tables."""
        var_state, var_hash = self.var_props.load(event)
        fp = self.get_fixed_props(event)
        if fp is None:
            return var_state, var_hash
        fixed_state, fixed_hash = fp.load(event)
        # Merge fixed_state and var_state, letting fixed_state
        # override var_state except when the value in fixed_state is
        # None.
        res = []
        placement = {}  # property name -> placement in results
        for rec in fixed_state:
            placement[rec[0]] = len(res)
            res.append(rec)
        for rec in var_state:
            index = placement.get(rec[0])
            if index is None:
                res.append(rec)
            elif res[index][2] is None:
                # override the fixed value, since it was None.
                res[index] = rec
        return res, (fixed_hash, var_hash)


    def store(self, event, state):
        """Stores state in two tables."""
        fp = self.get_fixed_props(event)
        if fp is None:
            return self.var_props.store(event, state)
        # Store the fixed state first and find out what got left over.
        leftover = {}
        state = list(state)
        state.sort()
        fixed_hash = fp.store(event, state, leftover=leftover)
        if leftover:
            var_state = []
            for prop_name, (typ, value) in leftover.items():
                var_state.append((prop_name, typ, value))
            var_hash = self.var_props.store(event, var_state)
        else:
            var_hash = ()
        return (fixed_hash, var_hash)
