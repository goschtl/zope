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
"""Gateways for storing security information.

$Id$
"""

from apelib.core.interfaces import IGateway, MappingError
from apelib.core.schemas import RowSequenceSchema
from params import string_to_params, params_to_string

from base import FSGatewayBase


class FSSecurityAttributes (FSGatewayBase):
    """Gateway for storing security attributes."""

    __implements__ = IGateway

    schema = RowSequenceSchema()
    schema.add('declaration_type', 'string')
    schema.add('role', 'string')
    schema.add('permission', 'string')
    schema.add('username', 'string')

    def __init__(self, annotation='security', conn_name='fs'):
        self.annotation = annotation
        FSGatewayBase.__init__(self, conn_name)

    def load(self, event):
        fs_conn = self.get_connection(event)
        text = fs_conn.read_annotation(event.oid, self.annotation, '')
        res = []
        if text:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                params = string_to_params(line)
                if params:
                    decl_type = params[0][0]
                    row = [decl_type, '', '', '']
                    for k, v in params[1:]:
                        k = k.lower()
                        if '_' in k:
                            # temporary backward compatibility
                            k = k.split('_', 1)[0]
                        if k == 'role':
                            row[1] = v
                        elif k == 'permission':
                            row[2] = v
                        elif k == 'username':
                            row[3] = v
                        else:
                            raise ValueError(
                                "Could not read security declaration "
                                "%s for %s" % (repr(line), repr(event.oid)))
                    res.append(tuple(row))
        res.sort()
        return res, tuple(res)


    def store(self, event, state):
        lines = []
        for d, r, p, u in state:
            params = [(d, '')]
            if r:
                params.append(('role', r))
            if p:
                params.append(('permission', p))
            if u:
                params.append(('username', u))
            s = params_to_string(params)
            lines.append(s)
        if lines:
            lines.sort()
            text = '\n'.join(lines)
            fs_conn = self.get_connection(event)
            fs_conn.write_annotation(event.oid, self.annotation, text)
        state = list(state)
        state.sort()
        return tuple(state)



class FSUserList (FSGatewayBase):
    """User list gateway, where the user list is stored in a flat file."""

    __implements__ = IGateway

    schema = RowSequenceSchema()
    schema.add('id', 'string', 1)
    schema.add('password', 'string')
    schema.add('roles', 'string:list')
    schema.add('domains', 'string:list')

    def load(self, event):
        c = self.get_connection(event)
        assert c.read_node_type(event.oid) == 'f'
        text = c.read_data(event.oid)
        res = []
        for line in text.split('\n'):
            L = line.strip()
            if not L.startswith('#') and ':' in L:
                id, password, rolelist, domainlist = L.split(':', 3)
                roles = self._split_list(rolelist)
                domains = self._split_list(domainlist)
                res.append((id, password, roles, domains))
        res.sort()
        return res, text


    def _split_list(self, s):
        return tuple([item.strip() for item in s.split(',') if item])


    def _join_list(self, items):
        for item in items:
            if item.strip() != item:
                raise MappingError(
                    "Leading and trailing whitespace are not allowed "
                    "in roles and domains")
            item = item.strip()
            if not item:
                raise MappingError("Empty role or domain not allowed")
            if ',' in item or ':' in item or '\n' in item:
                raise MappingError(
                    "Commas, colons, and newlines are not allowed "
                    "in roles and domains")
        return ','.join(items)


    def store(self, event, state):
        replace_lines = {}
        for id, password, roles, domains in state:
            if ':' in id or '\n' in id:
                raise MappingError('User IDs cannot have colons or newlines')
            if id.startswith('#'):
                raise MappingError('User IDs cannot start with #')
            if ':' in password or '\n' in password:
                raise MappingError('Passwords cannot have colons or newlines')
            rolelist = self._join_list(roles)
            domainlist = self._join_list(domains)
            to_write = '%s:%s:%s:%s' % (id, password, rolelist, domainlist)
            replace_lines[id] = to_write
        oid = event.oid
        fs_conn = self.get_connection(event)
        fs_conn.write_node_type(oid, 'f')
        # Read the existing text only to maintain the current order.
        text = fs_conn.read_data(oid, allow_missing=1)
        if text is None:
            text = ''
        new_lines = []
        # Replace / remove users
        for line in text.split('\n'):
            L = line.strip()
            if not L.startswith('#'):
                if ':' in L:
                    name, stuff = L.split(':', 1)
                    replace = replace_lines.get(name, '')
                    if replace and replace != L:
                        new_lines.append(replace)
                        del replace_lines[name]
                # else remove the line
            else:
                new_lines.append(line)
        # Append new users
        for line in replace_lines.values():
            new_lines.append(line)
        # Write it
        text = '\n'.join(new_lines)
        fs_conn.write_data(oid, text)
        serial = list(state)
        serial.sort()
        return text
