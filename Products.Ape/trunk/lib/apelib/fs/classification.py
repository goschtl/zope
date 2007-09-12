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
"""Filesystem classification annotation.

$Id$
"""

from apelib.core.interfaces import IGateway, LoadError, OIDConflictError
from apelib.core.schemas import ColumnSchema

from base import FSGatewayBase


class FSClassificationAnnotation(FSGatewayBase):
    """Gateway for storing classification data."""

    __implements__ = IGateway

    schema = ColumnSchema('classification', 'classification')

    def load(self, event):
        fs_conn = self.get_connection(event)
        oid = event.oid
        classification = {'node_type': fs_conn.read_node_type(oid)}
        text = fs_conn.read_annotation(oid, 'classification', '')
        if text:
            lines = text.split('\n')
            for line in lines:
                if '=' in line:
                    k, v = line.split('=', 1)
                    classification[k.strip()] = v.strip()
        classification['extension'] = fs_conn.read_extension(oid)
        classification['subpath'] = fs_conn.get_subpath(oid)
        return classification, text.strip()

    def store(self, event, state):
        # state is a classification
        fs_conn = self.get_connection(event)
        oid = event.oid
        if event.is_new:
            # Don't overwrite existing data
            try:
                fs_conn.read_node_type(oid)
            except LoadError:
                # Nothing exists yet.
                pass
            else:
                # Something exists.  Don't overwrite it.
                raise OIDConflictError(oid)
        items = state.items()
        items.sort()
        text = []
        for k, v in items:
            if k == 'extension':
                fs_conn.suggest_extension(oid, v)
            else:
                text.append('%s=%s' % (k, v))
        text = '\n'.join(text)
        fs_conn.write_annotation(oid, 'classification', text)
        return text.strip()
