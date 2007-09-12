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
"""SQL classification gateway

$Id$
"""

from apelib.core.schemas import ColumnSchema, RowSequenceSchema
from apelib.core.interfaces import OIDConflictError
from sqlbase import SQLGatewayBase


class SQLClassification (SQLGatewayBase):

    __implements__ = SQLGatewayBase.__implements__

    schema = ColumnSchema('classification', 'classification')
    table_name = 'classification'
    table_schema = RowSequenceSchema()
    table_schema.add('class_name', 'string', 0)
    table_schema.add('mapper_name', 'string', 0)

    def load(self, event):
        table = self.get_table(event)
        rows = table.select(self.column_names, oid=event.oid)
        classification = {}
        if rows:
            rec = rows[0]
            if rec[0]:
                classification['class_name'] = rec[0]
            if rec[1]:
                classification['mapper_name'] = rec[1]
        else:
            raise KeyError(event.oid)
        return classification, rec

    def store(self, event, classification):
        conn = self.get_connection(event)
        table = self.get_table(event)
        row = (classification.get('class_name', ''),
               classification.get('mapper_name', ''))
        try:
            table.set_one(event.oid, self.column_names, row, event.is_new)
        except conn.module.DatabaseError:
            raise OIDConflictError(event.oid)
        return row
