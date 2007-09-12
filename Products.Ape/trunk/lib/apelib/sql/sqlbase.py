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
"""Abstract gateways

$Id$
"""

from apelib.core.interfaces \
     import IGateway, IDatabaseInitializer, IDatabaseInitEvent
from apelib.core.schemas import ColumnSchema, RowSequenceSchema
from interfaces import IRDBMSConnection


class SQLGatewayBase:
    """SQL gateway base class"""

    __implements__ = IGateway, IDatabaseInitializer

    # override these in subclasses
    table_name = None
    schema = None
    table_schema = None
    oid_columns = [ColumnSchema('oid', 'int', 1)]

    def __init__(self, conn_name='db'):
        self.conn_name = conn_name
        if self.table_schema is None:
            if self.schema is not None:
                self.table_schema = self.schema
            else:
                self.table_schema = RowSequenceSchema()
        self.column_names = [f.name for f in self.table_schema.get_columns()]

    def get_connection(self, event):
        return event.connections[self.conn_name]

    def get_table(self, event):
        c = event.connections[self.conn_name]
        return c.get_table(self.table_name)

    def create(self, event):
        self.get_table(event).create()

    def init(self, event):
        conn = self.get_connection(event)
        assert IRDBMSConnection.isImplementedBy(conn)
        all = RowSequenceSchema(
            self.oid_columns + self.table_schema.get_columns())
        table = conn.define_table(self.table_name, all)
        if conn.exists(self.table_name, 'table'):
            if IDatabaseInitEvent.isImplementedBy(event) and event.clear_all:
                table.delete_rows()
        else:
            table.create()

    def load(self, event):
        raise NotImplementedError, "abstract method"

    def store(self, event, obj):
        raise NotImplementedError, "abstract method"

    def get_sources(self, event):
        return None
