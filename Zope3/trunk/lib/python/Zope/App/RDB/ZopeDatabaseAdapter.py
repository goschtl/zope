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
"""The connection adapters contained by ConnectionService.

$Id: ZopeDatabaseAdapter.py,v 1.8 2002/11/08 12:46:58 stevea Exp $
"""
from types import StringTypes
from Persistence import Persistent
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter
from Zope.App.RDB.ZopeConnection import ZopeConnection


class DatabaseAdapterError(Exception):
    pass


class ZopeDatabaseAdapter(Persistent):

    __implements__ = IZopeDatabaseAdapter
    _v_connection =  None

    def __init__(self, dsn):
        self.setDSN(dsn)
        
    def _connection_factory(self):
        """This method should be overwritten by all subclasses"""
        conn_info = parseDSN(self.dsn)
        
    ############################################################
    # Implementation methods for interface
    # Zope.App.RDB.IZopeDatabaseAdapter.

    def setDSN(self, dsn):
        'See Zope.App.RDB.IZopeDatabaseAdapter.IZopeDatabaseAdapter'
        assert dsn.startswith('dbi://'), "The DSN has to start with 'dbi://'"
        self.dsn = dsn

    def getDSN(self):
        'See Zope.App.RDB.IZopeDatabaseAdapter.IZopeDatabaseAdapter'
        return self.dsn

    def connect(self):
        'See Zope.App.RDB.IZopeDatabaseAdapter.IZopeDatabaseAdapter'
        if not self.isConnected():
            self._v_connection = ZopeConnection(self._connection_factory(),
                                                self)

    def disconnect(self):
        'See Zope.App.RDB.IZopeDatabaseAdapter.IZopeDatabaseAdapter'
        if self.isConnected():
           self._v_connection.close()
           self._v_connection = None

    def isConnected(self):
        'See Zope.App.RDB.IZopeDatabaseAdapter.IZopeDatabaseAdapter'
        return hasattr(self, '_v_connection') and \
               self._v_connection is not None

    def __call__(self):
        'See Zope.App.RDB.IZopeDatabaseAdapter.IZopeDatabaseAdapter'
        self.connect()
        return self._v_connection

    #
    ############################################################

    ############################################################
    # Implementation methods for interface
    # Zope.App.RDB.IDBITypeInfo.IDBITypeInfo

    # Pessimistic defaults
    paramstyle = 'pyformat'
    threadsafety = 0

    def getConverter(self, type):
        'See Zope.App.RDB.IDBITypeInfo.IDBITypeInfo'
        return identity

    #
    ############################################################

def identity(x):
    return x

def parseDSN(dsn):
    """We could have the following cases:

       dbi://dbname
       dbi://dbname;param1=value...
       dbi://user:passwd/dbname
       dbi://user:passwd/dbname;param1=value...
       dbi://user:passwd@host:port/dbname
       dbi://user:passwd@host:port/dbname;param1=value...
    """
    assert isinstance(dsn, StringTypes), 'The dsn is not a string.'
    assert dsn.startswith('dbi://'), 'Invalid DSN; must start with "dbi://"'

    result = {}

    dsn = dsn[6:]
    # Get parameters (dict) from DSN
    raw_params = dsn.split(';')
    dsn = raw_params[0]
    raw_params = raw_params[1:]

    parameters = dict([param.split('=') for param in raw_params])

    result['parameters'] = parameters

    # Get the dbname from the DSN
    if dsn.find('/') > 0:
        dsn, dbname = dsn.split('/')
    else:
        dbname = dsn
        dsn = ''

    result['dbname'] = dbname

    # Get host and port from DSN
    if dsn and dsn.find('@') > 0:
        dsn, host_port = dsn.split('@')
        host, port = host_port.split(':')
    else:
        host, port = '', ''

    result['host'] = host
    result['port'] = port
    
    # Get username and password from DSN
    if dsn:
        username, password = dsn.split(':')
    else:
        username, password = '', ''

    result['username'] = username
    result['password'] = password

    return result






