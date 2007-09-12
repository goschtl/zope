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
"""SQL gateways for security information.

$Id$
"""

from apelib.core.schemas import RowSequenceSchema, ColumnSchema
from sqlbase import SQLGatewayBase


class SQLSecurityAttributes (SQLGatewayBase):
    """SQL security attribute storage"""

    __implements__ = SQLGatewayBase.__implements__

    schema = RowSequenceSchema()
    schema.add('declaration_type', 'string')
    schema.add('role', 'string')
    schema.add('permission', 'string')
    schema.add('username', 'string')

    table_name = 'security'
    oid_columns = [ColumnSchema('oid', 'int', 0)]  # Don't create a primary key

    def load(self, event):
        table = self.get_table(event)
        items = table.select(self.column_names, oid=event.oid)
        items.sort()
        return items, tuple(items)

    def store(self, event, state):
        table = self.get_table(event)
        table.set_many(event.oid, (), self.column_names, state)
        state = list(state)
        state.sort()
        return tuple(state)



class SQLUserList (SQLGatewayBase):
    """Stores and retrieves all users for a folder at once."""

    __implements__ = SQLGatewayBase.__implements__

    schema = RowSequenceSchema()
    schema.add('id', 'string', 1)
    schema.add('password', 'string')
    schema.add('roles', 'string:list')
    schema.add('domains', 'string:list')

    table_defs = {
        'users':        [('oid', 'int', 1),
                         ('id', 'string', 1),
                         ('password', 'string', 0)],
        'user_roles':   [('oid', 'int', 0),
                         ('id', 'string', 0),
                         ('role', 'string', 0)],
        'user_domains': [('oid', 'int', 0),
                         ('id', 'string', 0),
                         ('domain', 'string', 0)],
        }


    def init(self, event):
        conn = self.get_connection(event)
        for table_name, columns in self.table_defs.items():
            table_schema = RowSequenceSchema()
            for args in columns:
                table_schema.add(*args)
            table = conn.define_table(table_name, table_schema)
            if not conn.exists(table_name, 'table'):
                table.create()
            elif event.clear_all:
                table.delete_rows()


    def load(self, event):
        conn = self.get_connection(event)
        rows = conn.get_table('users').select(
            ('id', 'password'), oid=event.oid)
        data = {}
        for id, password in rows:
            data[id] = (password, [], [])
        rows = conn.get_table('user_roles').select(
            ('id', 'role'), oid=event.oid)
        for id, role in rows:
            row = data.get(id)
            if row is not None:
                row[1].append(role)
        rows = conn.get_table('user_domains').select(
            ('id', 'domain'), oid=event.oid)
        for id, domain in rows:
            row = data.get(id)
            if row is not None:
                row[2].append(domain)
        records = []
        for id, (password, roles, domains) in data.items():
            roles = list(roles)
            roles.sort()
            domains = list(domains)
            domains.sort()
            records.append((id, password, tuple(roles), tuple(domains)))
        records.sort()
        return records, tuple(records)


    def store(self, event, state):
        oid = event.oid
        conn = self.get_connection(event)
        rows = [(id, pw) for id, pw, roles, domains in state]
        conn.get_table('users').set_many(
            event.oid, (), ('id', 'password',), rows)
        roles_d = {}
        domains_d = {}
        for id, pw, roles, domains in state:
            for role in roles:
                roles_d[(id, role)] = 1
            for domain in domains:
                domains_d[(id, domain)] = 1
        conn.get_table('user_roles').set_many(
            event.oid, (), ('id', 'role',), roles_d.keys())
        conn.get_table('user_domains').set_many(
            event.oid, (), ('id', 'domain',), domains_d.keys())
        state = list(state)
        state.sort()
        return tuple(state)
