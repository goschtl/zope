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
"""SQL gateways for a filesystem-like tree structure.

$Id$
"""

from apelib.core.schemas import ColumnSchema, RowSequenceSchema
from sqlbase import SQLGatewayBase


class SQLObjectData (SQLGatewayBase):
    """SQL object data gateway"""

    __implements__ = SQLGatewayBase.__implements__

    schema = ColumnSchema('data', 'string')
    table_name = 'object_data'
    table_schema = RowSequenceSchema()
    table_schema.add('data', 'blob', 0)

    def load(self, event):
        table = self.get_table(event)
        firstcol = self.column_names[:1]
        items = table.select(firstcol, oid=event.oid)
        if items:
            state = str(items[0][0])
        else:
            state = ''
        return state, state

    def store(self, event, state):
        conn = self.get_connection(event)
        table = self.get_table(event)
        firstcol = self.column_names[:1]
        data = (state,)
        table.set_one(event.oid, firstcol, data, event.is_new)
        return state


class SQLFolderItems (SQLGatewayBase):
    """SQL folder items gateway"""

    __implements__ = SQLGatewayBase.__implements__

    schema = RowSequenceSchema()
    schema.add('key', 'string', 1)
    schema.add('oid', 'string')
    schema.add('classification', 'classification')
    table_name = 'folder_items'
    table_schema = RowSequenceSchema()
    table_schema.add('name', 'string', 1)
    table_schema.add('child_oid', 'int', 0)

    def load(self, event):
        table = self.get_table(event)
        rows = table.select(self.column_names, oid=event.oid)
        res = []
        h = []
        for name, child_oid in rows:
            s = str(child_oid)
            classification = event.classify(s)
            res.append((name, s, classification))
            h.append((name, long(child_oid)))
        h.sort()
        return res, tuple(h)

    def store(self, event, state):
        table = self.get_table(event)
        rows = [(name, long(child_oid)) for (name, child_oid, cls) in state]
        rows.sort()
        # Note that set_many() requires the child_oid column to match
        # its database type.
        table.set_many(event.oid, ('name',), ('child_oid',), rows)
        return tuple(rows)


class SQLItemId (SQLGatewayBase):
    """SQL item ID gateway.

    Piggybacks SQLFolderItems for init and store.
    Makes the assumption that the item is stored in only one place.
    """

    __implements__ = SQLGatewayBase.__implements__

    schema = ColumnSchema('id', 'string')
    table_name = 'folder_items'
    table_schema = RowSequenceSchema()
    table_schema.add('child_oid', 'int', 1)
    table_schema.add('name', 'string', 0)

    def init(self, event):
        pass

    def load(self, event):
        table = self.get_table(event)
        rows = table.select(('name',), child_oid=event.oid)
        if len(rows) >= 1:
            name = rows[0][0]  # Accept only the first result
        else:
            name = None
        # Disable conflict checking by returning None as the hash value.
        return name, None

    def store(self, event, state):
        return None


class SQLRemainder (SQLObjectData):
    """SQL remainder pickle gateway"""

    __implements__ = SQLGatewayBase.__implements__

    table_name = 'remainder'
    table_schema = RowSequenceSchema()
    table_schema.add('pickle', 'blob', 0)


class SQLModTime (SQLGatewayBase):
    """SQL object mod time gateway"""

    __implements__ = SQLGatewayBase.__implements__

    schema = ColumnSchema('mtime', 'int')  # second
    table_name = 'mtime'
    table_schema = RowSequenceSchema()
    table_schema.add('mtime', 'long', 0)

    def load(self, event):
        table = self.get_table(event)
        items = table.select(self.column_names, oid=event.oid)
        if items:
            state = long(items[0][0])
        else:
            state = 0L
        return state, state

    def store(self, event, state):
        state = long(state)
        table = self.get_table(event)
        data = (state,)
        table.set_one(event.oid, self.column_names, data, event.is_new)
        return state


def root_mapping():
    """Returns a gateway suitable for storing the root persistent mapping.
    """
    from apelib.core.gateways import CompositeGateway
    g = CompositeGateway()
    g.add('references', SQLFolderItems())
    g.add('others', SQLObjectData())
    return g
