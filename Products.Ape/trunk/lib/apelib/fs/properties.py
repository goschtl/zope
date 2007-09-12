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
"""Filesystem property gateways.

$Id$
"""

from types import StringType

from apelib.core.interfaces import IGateway
from apelib.core.schemas import ColumnSchema, RowSequenceSchema

from base import FSGatewayBase


token_replacements = {
    '\\\\': '\\',
    '\\t': '\t',
    '\\r': '\r',
    '\\n': '\n',
    }

def escape_string(s):
    return s.replace('\\', '\\\\').replace('\n', '\\n').replace(
        '\r', '\\r').replace('\t', '\\t')

def unescape_string(s):
    res = []
    pos = 0
    while 1:
        p = s.find('\\', pos)
        if p >= 0:
            res.append(s[pos:p])
            token = s[p:p+2]
            c = token_replacements.get(token)
            if c is not None:
                # known escape sequence
                res.append(c)
            else:
                # unknown sequence
                res.append(token)
            pos = p + 2
        else:
            res.append(s[pos:])
            break
    return ''.join(res)


class FSProperties (FSGatewayBase):
    """Simple properties to filesystem properties annotation gateway.
    """

    __implements__ = IGateway

    schema = RowSequenceSchema()
    schema.add('id', 'string', 1)
    schema.add('type', 'string')
    schema.add('data', 'string')

    def __init__(self, annotation='properties', conn_name='fs'):
        self.annotation = str(annotation)
        FSGatewayBase.__init__(self, conn_name)

    def load(self, event):
        fs_conn = self.get_connection(event)
        text = fs_conn.read_annotation(event.oid, self.annotation, '')
        res = []
        if text:
            lines = text.split('\n')
            for line in lines:
                if '=' in line:
                    k, v = line.split('=', 1)
                    if ':' in k:
                        k, t = k.split(':', 1)
                    else:
                        t = 'string'
                    res.append((k, t, unescape_string(v)))
        res.sort()
        return res, tuple(res)

    def store(self, event, state):
        lines = []
        for k, t, v in state:
            lines.append('%s:%s=%s' % (k, t, escape_string(v)))
        lines.sort()
        text = '\n'.join(lines)
        fs_conn = self.get_connection(event)
        fs_conn.write_annotation(event.oid, self.annotation, text)
        state = list(state)
        state.sort()
        return tuple(state)


class FSAnnotationData (FSGatewayBase):
    """Text to filesystem property annotation gateway."""

    __implements__ = IGateway

    schema = ColumnSchema('data', 'string')

    def __init__(self, annotation, conn_name='fs'):
        self.annotation = str(annotation)
        FSGatewayBase.__init__(self, conn_name)

    def load(self, event):
        fs_conn = self.get_connection(event)
        state = fs_conn.read_annotation(event.oid, self.annotation, '').strip()
        return state, state

    def store(self, event, state):
        if not isinstance(state, StringType):
            raise ValueError('Not a string: %s' % repr(state))
        state = state.strip()
        if state:
            fs_conn = self.get_connection(event)
            fs_conn.write_annotation(event.oid, self.annotation, state)
        return state
