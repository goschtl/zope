##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Gadfly Database Adapter (batteries included)

$Id$
"""
import gadfly
import os

from zope.app.rdb import ZopeDatabaseAdapter, parseDSN
from zope.app.rdb import DatabaseAdapterError

GadflyError = DatabaseAdapterError


class GadflyAdapter(ZopeDatabaseAdapter):
    """A Gadfly adapter for Zope3"""

    # The registerable object needs to have a container
    __name__ = __parent__ = None 
    
    def _connection_factory(self):
        """Create a Gadfly DBI connection based on the DSN.

        Only local (filesystem-based) Gadfly connections are supported
        at this moment."""

        conn_info = parseDSN(self.dsn)
        if conn_info['host'] != '' or conn_info['username'] != '' or \
           conn_info['port'] != '' or conn_info['password'] != '':
            raise DatabaseAdapterError(
                "DSN for GadflyDA must be of the form "
                "dbi://dbname or dbi://dbname;dir=directory."
                )

        connection = conn_info['dbname']
        dir = os.path.join(getGadflyRoot(),
                           conn_info['parameters'].get('dir', connection))

        if not os.path.isdir(dir):
            raise DatabaseAdapterError, 'Not a directory ' + dir

        if not os.path.exists(os.path.join(dir, connection + ".gfd")):
            db = gadfly.gadfly()
            db.startup(connection, dir)
        else:
            db = gadfly.gadfly(connection, dir)

        return db

_gadflyRoot = 'gadfly'

def setGadflyRoot(path='gadfly'):
    global _gadflyRoot
    _gadflyRoot = path

def getGadflyRoot():
    global _gadflyRoot
    return _gadflyRoot
