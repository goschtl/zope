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
"""Zope RDBMS Transaction Integration.

Provides a proxy for interaction between the zope transaction
framework and the db-api connection. Databases which want to support
sub transactions need to implement their own proxy.

$Id: __init__.py,v 1.4 2002/12/31 18:36:13 jeremy Exp $
"""
from types import StringTypes

from persistence import Persistent

from transaction import get_transaction
from transaction.interfaces import IDataManager

from zope.security import checker

from zope.app.interfaces.rdb import DatabaseException
from zope.app.interfaces.rdb import IResultSet, ISQLCommand
from zope.app.interfaces.rdb import IZopeConnection, IZopeCursor
from zope.app.interfaces.rdb import IZopeDatabaseAdapter

from zope.app.component.nextservice import getNextService


class ResultSet(list):
    """Database Result Set.

    Currently we don't do lazy instantation of rows.
    """

    __implements__ = IResultSet
    __slots__ = ('columns',)

    def __init__(self, columns, rows):
        self.columns = tuple(columns)
        row_class = RowClassFactory(columns)
        super(ResultSet, self).__init__(map(row_class, rows))

    __safe_for_unpickling__ = True

    def __reduce__(self):
        cols = self.columns
        return (ResultSet,
                (cols, [[getattr(row, col) for col in cols] for row in self])
               )
                
    def __cmp__(self, other):
        if not isinstance(other, ResultSet):
            return super(ResultSet, self).__cmp__(other)
        c = cmp(self.columns, other.columns)
        if c:
            return c
        for row, other_row in zip(self, other):
            c = cmp(row, other_row)
            if c:
                return c
        return cmp(len(self), len(other))


class SQLCommand:
    """A simple version of a SQL Command."""

    __implements__ = ISQLCommand

    def __init__(self, connection_name='', sql=''):
        self.connectionName = connection_name
        self.sql = sql

    def getConnection(self):
        'See ISQLCommand'
        connection_service = getNextService(self, "SQLDatabaseConnections")
        connection = connection_service.getConnection(self.connectionName)
        return connection

    def __call__(self):
        return queryForResults(self.getConnection(), self.sql)


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

    def setDSN(self, dsn):
        'See IZopeDatabaseAdapter'
        assert dsn.startswith('dbi://'), "The DSN has to start with 'dbi://'"
        self.dsn = dsn

    def getDSN(self):
        'See IZopeDatabaseAdapter'
        return self.dsn

    def connect(self):
        'See IZopeDatabaseAdapter'
        if not self.isConnected():
            self._v_connection = ZopeConnection(self._connection_factory(),
                                                self)

    def disconnect(self):
        'See IZopeDatabaseAdapter'
        if self.isConnected():
            self._v_connection.close()
            self._v_connection = None

    def isConnected(self):
        'See IZopeDatabaseAdapter'
        return hasattr(self, '_v_connection') and \
               self._v_connection is not None

    def __call__(self):
        'See IZopeDatabaseAdapter'
        self.connect()
        return self._v_connection

    # Pessimistic defaults
    paramstyle = 'pyformat'
    threadsafety = 0

    def getConverter(self, type):
        'See IDBITypeInfo'
        return identity

def identity(x):
    return x

def parseDSN(dsn):
    """Parses a database connection string.

    We could have the following cases:

       dbi://dbname
       dbi://dbname;param1=value...
       dbi://user:passwd/dbname
       dbi://user:passwd/dbname;param1=value...
       dbi://user:passwd@host:port/dbname
       dbi://user:passwd@host:port/dbname;param1=value...

    Return value is a mapping with the following keys:

       username     username (if given) or an empty string
       password     password (if given) or an empty string
       host         host (if given) or an empty string
       port         port (if given) or an empty string
       dbname       database name
       parameters   a mapping of additional parameters to their values
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


class ZopeCursor:
    __implements__ = IZopeCursor

    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def execute(self, operation, parameters=None):
        """Executes an operation, registering the underlying
        connection with the transaction system.  """

        if isinstance(operation, unicode):
            operation = operation.encode('UTF-8')
        if parameters is None:
            parameters = {}
        self.connection.registerForTxn()
        return self.cursor.execute(operation, parameters)

    def __getattr__(self, key):
        return getattr(self.cursor, key)

    def fetchone(self):
        results = self.cursor.fetchone()
        return self._convertTypes(results)

    def fetchmany(self, *args, **kw):
        results = self.cursor.fetchmany(*args, **kw)
        return self._convertTypes(results)

    def fetchall(self):
        results = self.cursor.fetchall()
        return self._convertTypes(results)

    def _convertTypes(self, results):
        "Perform type conversion on query results"
        getConverter = self.connection.getTypeInfo().getConverter
        converters = [getConverter(col_info[1])
                      for col_info in self.cursor.description]
## A possible optimization -- need benchmarks to check if it is worth it
##      if filter(lambda x: x is not ZopeDatabaseAdapter.identity, converters):
##          return results  # optimize away
        def convertRow(row):
            return map(lambda converter, value: converter(value),
                       converters, row)
        return map(convertRow, results)


class ZopeConnection:

    __implements__ =  IZopeConnection

    def __init__(self, conn, typeinfo):
        self.conn = conn
        self._txn_registered = False
        self._type_info = typeinfo

    def __getattr__(self, key):
        # The IDBIConnection interface is hereby implemented
        return getattr(self.conn, key)

    def cursor(self):
        'See IZopeConnection'
        return ZopeCursor(self.conn.cursor(), self)

    def registerForTxn(self):
        'See IZopeConnection'
        if not self._txn_registered:
            tm = ZopeDBTransactionManager(self)
            get_transaction().join(tm)
            self._txn_registered = True

    def commit(self):
        'See IDBIConnection'
        self._txn_registered = False
        self.conn.commit()


    def rollback(self):
        'See IDBIConnection'
        self._txn_registered = False
        self.conn.rollback()

    def getTypeInfo(self):
        'See IDBITypeInfoProvider'
        return self._type_info


def queryForResults(conn, query):
    """Convenience function to quickly execute a query."""

    # XXX need to do typing
    cursor = conn.cursor()

    try:
        cursor.execute(query)
    except Exception, error:
        raise DatabaseException(str(error))

    if cursor.description is not None:
        columns = [c[0] for c in cursor.description]
        results = cursor.fetchall()
    else:
        # Handle the case that the query was not a SELECT
        columns = []
        results = []

    return ResultSet(columns, results)


class ZopeDBTransactionManager:

    __implements__ =  IDataManager

    def __init__(self, dbconn):
        self._dbconn = dbconn

    def prepare(self, txn):
        return True

    def abort(self, txn):
        self._dbconn.rollback()

    def commit(self, txn):
        self._dbconn.commit()

    # XXX Do any of the Python DB-API implementations support
    # two-phase commit?

    def savepoint(self, txn):
        return None


class Row(object):
    """Represents a row in a ResultSet"""

    def __init__(self, data):
        for k, v in zip(self.__slots__, data):
            setattr(self, k, v)

    def __str__(self):
        return "row class %s" % str(self.__slots__)

    def __cmp__(self, other):
        if not isinstance(other, Row):
            return super(Row, self).__cmp__(other)
        c = cmp(self.__slots__, other.__slots__)
        if c:
            return c
        for column in self.__slots__:
            c = cmp(getattr(self, column), getattr(other, column))
            if c:
                return c
        return 0


def RowClassFactory(columns):
    """Creates a Row object"""
    klass_namespace = {}

    klass_namespace['__Security_checker__'] = checker.NamesChecker(columns)
    klass_namespace['__slots__'] = tuple(columns)

    return type('GeneratedRowClass', (Row,), klass_namespace)
