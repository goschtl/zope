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
$Id: ZopeCursor.py,v 1.4 2002/11/05 12:15:28 alga Exp $
"""
from types import UnicodeType
from IZopeCursor import IZopeCursor

class ZopeCursor:
    __implements__ = IZopeCursor

    def __init__(self, cursor, connection):
        self.cursor = cursor
        self.connection = connection

    def execute(self, operation, parameters=None):
        """Executes an operation, registering the underlying
        connection with the transaction system.  """

        if isinstance(operation, UnicodeType):
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
