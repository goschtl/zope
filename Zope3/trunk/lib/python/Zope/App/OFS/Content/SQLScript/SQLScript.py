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
$Id: SQLScript.py,v 1.7 2002/08/08 15:05:59 ersab Exp $
"""
from types import StringTypes

from Persistence import Persistent
from Zope.ComponentArchitecture import getService
from Zope.ContextWrapper import ContextMethod

from Zope.DocumentTemplate.DT_HTML import HTML
from Zope.App.Traversing import getParent
from Zope.App.RDB.SQLCommand import SQLCommand
from Zope.App.RDB.Util import queryForResults

from Zope.App.OFS.Content.IFileContent import IFileContent
from Zope.App.OFS.Content.SQLScript.ISQLScript import ISQLScript
from Zope.App.OFS.Content.SQLScript.Arguments import parseArguments

from DT_SQLVar import SQLVar
from DT_SQLTest import SQLTest
from DT_SQLGroup import SQLGroup

from time import time

try: from Persistence.BTrees.IOBTree import IOBucket as Bucket
except: Bucket = lambda:{}


class SQLDTML(HTML):
    __name__ = 'SQLDTML'

    commands = {}

    for k, v in HTML.commands.items():
        commands[k]=v

    # add the new tags to the DTML
    commands['sqlvar' ] = SQLVar
    commands['sqltest'] = SQLTest
    commands['sqlgroup' ] = SQLGroup


class SQLScript(SQLCommand, Persistent):

    __implements__ = ISQLScript, IFileContent

    def __init__(self, connectionName='', source='', arguments='',
                 maxCache=0, cacheTime=0):
        self.template = SQLDTML(source)
        self.setConnectionName(connectionName)
        # In our case arguments should be a string that is parsed
        self.setArguments(arguments)
        self.setMaxCache(maxCache)
        self.setCacheTime(cacheTime)

    def setArguments(self, arguments):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        assert isinstance(arguments, StringTypes), \
               '"arguments" argument of setArguments() must be a string'
        self._arg_string = arguments
        self._arguments = parseArguments(arguments)

    def getArguments(self):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        return self._arguments

    def getArgumentsString(self):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        return self._arg_string

    def setSource(self, source):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        self.template.munge(source)

    def getSource(self):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        return self.template.read_raw()

    def getTemplate(self):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        return self.template

    def setConnectionName(self, name):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        self._connectionName = name
        self._clearCache()

    def getConnectionName(self):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        return self._connectionName

    def setMaxCache(self, maxCache):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        self._maxCache = maxCache
        self._clearCache()

    def getMaxCache(self):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        return self._maxCache

    def setCacheTime(self, cacheTime):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        self._cacheTime = cacheTime
        self._clearCache()

    def getCacheTime(self):
        'See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript'
        return self._cacheTime

    def getConnection(self):
        'See Zope.App.RDB.ISQLCommand.ISQLCommand'
        connection_service = getService(self, "Connections")
        connection = connection_service.getConnection(self.connectionName)
        return connection

    getConnection = ContextMethod(getConnection)

    def __call__(self, **kw):
        'See Zope.App.RDB.ISQLCommand.ISQLCommand'

        # Try to resolve arguments
        arg_values = {}
        missing = []
        for name in self._arguments.keys():
            name = name.encode('UTF-8')
            try:
                # Try to find argument in keywords
                arg_values[name] = kw[name]
            except:
                # Okay, the first try failed, so let's try to find the default
                arg = self._arguments[name]
                try:
                    arg_values[name] = arg['default']
                except:
                    # Now the argument might be optional anyways; let's check
                    try:
                        if not arg['optional']:
                            missing.append(name)
                    except:
                        missing.append(name)

        try:
            connection = self.getConnection()
        except AttributeError:
            raise AttributeError, (
                "The database connection **%s** cannot be found." % (
                self.connectionName))

        if connection is None:
            raise 'Database Error', (
                '%s is not connected to a database' %'foo')# self.id)

        query = apply(self.template, (), arg_values)

        if self._maxCache > 0 and self._cacheTime > 0:
            return self._cachedResult(connection, query)
        else:
            return queryForResults(connection, query)

    __call__ = ContextMethod(__call__)


    def _clearCache(self):
        'Clear the cache'
        self._v_cache = {}, Bucket()

    def _cachedResult(self, connection, query):
        'Try to fetch query result from cache'
        if not hasattr(self, '_v_cache'):
            self._clearCache()
        cache, tcache = self._v_cache
        max_cache = self._maxCache
        now = time()
        t = now - self._cacheTime
        if len(cache) > max_cache / 2:
            keys = tcache.keys()
            keys.reverse()
            while keys and (len(keys) > max_cache or keys[-1] < t):
                key = keys[-1]
                q = tcache[key]
                del tcache[key]
                if int(cache[q][0]) == key:
                    del cache[q]
                del keys[-1]

        if cache.has_key(query):
            k, r = cache[query]
            if k > t: return r

        result = queryForResults(connection, query)
        if self._cacheTime > 0:
            tcache[int(now)] = query
            cache[query] = now, result

        return result


    # See Zope.App.OFS.Content.SQLScript.ISQLScript.ISQLScript
    arguments = property(getArgumentsString, setArguments, None,
                         "Set the arguments that are used for the SQL Script.")
    source = property(getSource, setSource, None,
                      "Set the SQL template source.")
    connectionName = property(getConnectionName, setConnectionName, None,
                              "Connection Name for the SQL scripts.")
    maxCache = property(getMaxCache, setMaxCache, None,
                        "Set the size of the SQL Script cache.")
    cacheTime = property(getCacheTime, setCacheTime, None,
                         "Set the time in seconds that results are cached.")

