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
"""
Gadfly Database Adapter (batteries included)

$Id: Adapter.py,v 1.1 2002/11/05 17:34:39 alga Exp $
"""

import gadfly
import os

from Persistence import Persistent
from Zope.App.RDB.ZopeDatabaseAdapter import ZopeDatabaseAdapter, parseDSN
from Zope.App.RDB.ZopeDatabaseAdapter import DatabaseAdapterError
from Zope.App.RDB.ZopeConnection import ZopeConnection

GadflyError = DatabaseAdapterError


class GadflyAdapter(ZopeDatabaseAdapter):
    """A Gadfly adapter for Zope3"""
    
    __implements__ = ZopeDatabaseAdapter.__implements__

    def _getGadflyRoot(self):
	# XXX: Need to write a configuration directive for setting this up
	# At the moment gadfly root is 'gadfly' under the instance home (which
	# is assumed to be the current directory ATM).
        return 'gadfly'
    
    def _connection_factory(self):
        """Create a Gadfly DBI connection based on the DSN.

        Only local (filesystem-based) Gadfly connections are supported
        at this moment."""

        conn_info = parseDSN(self.dsn)
        if conn_info['host'] != '' or conn_info['username'] != '' or \
           conn_info['port'] != '' or conn_info['password'] != '':
            raise DatabaseAdapterError, "DSN for GadflyDA must be of the form " \
                  "dbi://dbname or dbi://dbname;dir=directory."

        connection = conn_info['dbname']
        dir = os.path.join(self._getGadflyRoot(),
                           conn_info['parameters'].get('dir', connection))

        if not os.path.isdir(dir):
            raise DatabaseAdapterError, 'Not a directory ' + dir

        if not os.path.exists(os.path.join(dir, connection + ".gfd")):
            db = gadfly.gadfly()
            db.startup(connection, dir)
        else:
            db = gadfly.gadfly(connection, dir)
            
        return db
