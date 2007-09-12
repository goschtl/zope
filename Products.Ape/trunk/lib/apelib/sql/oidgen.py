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
"""SQL OID generator

$Id$
"""

from apelib.core import interfaces

import sqlbase


class SQLOIDGenerator (sqlbase.SQLGatewayBase):

    __implements__ = (interfaces.IOIDGenerator,
                      interfaces.IDatabaseInitializer)

    table_name = 'oid_seq'
    root_oid = "0"

    def init(self, event):
        conn = self.get_connection(event)
        if not conn.exists(self.table_name, 'sequence'):
            conn.create_sequence(self.table_name, start=1)
        elif event.clear_all:
            conn.reset_sequence(self.table_name, start=1)

    def new_oid(self, event):
        """Returns a new OID.  Must return a string."""
        assert interfaces.IGatewayEvent.isImplementedBy(event)
        conn = self.get_connection(event)
        n = conn.increment(self.table_name)
        return str(n)
