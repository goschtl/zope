##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""DT_SQLVar Tests

$Id$
"""
import unittest
from zope.interface import implements, classImplements
from zope.component import getService
from zope.component.service import serviceManager as sm

from zope.app.tests import ztapi
from zope.app.rdb.interfaces import IConnectionService, IZopeDatabaseAdapter
from zope.app.rdb.interfaces import IZopeConnection
from zope.app.rdb.interfaces import IZopeCursor
from zope.app.servicenames import Adapters
from zope.app.component import nextservice
from zope.app.tests.placelesssetup import PlacelessSetup

from zope.app.annotation.interfaces import IAnnotatable, IAnnotations
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.attribute import AttributeAnnotations

from zope.app.cache.interfaces import ICacheable, ICache
from zope.app.cache.annotationcacheable import AnnotationCacheable
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.site.interfaces import ISimpleService

from zope.app.sqlscript.sqlscript import SQLScript, Arguments
from zope.app.sqlscript.interfaces import ISQLScript


# Make spme fixes, so that we overcome some of the natural ZODB properties
def getNextServiceManager(context):
    return sm

class CursorStub:

    implements(IZopeCursor)

    description = (('name', 'string'), ('counter', 'int'))
    count = 0

    def execute(self, operation, parameters=None):
        CursorStub.count += 1
        self.result = {"SELECT name, counter FROM Table WHERE id = 1":
                       (('stephan', CursorStub.count),),
                       "SELECT name, counter FROM Table WHERE id = 2":
                       (('marius', CursorStub.count),),
                       "SELECT name, counter FROM Table WHERE id = 3":
                       (('erik', CursorStub.count),)
                      }[operation]

    def fetchall(self):
        return self.result



class ConnectionStub:
    implements(IZopeConnection)

    def cursor(self):
        return CursorStub()


class ConnectionUtilityStub:
    implements(IZopeDatabaseAdapter)

    def __init__(self):
        self.connection = ConnectionStub()
        
    def __call__(self):
        return  self.connection
        
class ConnectionServiceStub:
    implements(IConnectionService, ISimpleService)

    def getConnection(self, name):
        return ConnectionStub()


class CacheStub:
    implements(ICache)
    def __init__(self):
        self.cache = {}

    def set(self, data, obj, key=None):
        if key:
            keywords = key.items()
            keywords.sort()
            keywords = tuple(keywords)
        self.cache[obj, keywords] = data

    def query(self, obj, key=None, default=None):
        if key:
            keywords = key.items()
            keywords.sort()
            keywords = tuple(keywords)
        return self.cache.get((obj, keywords), default)


class LocatableStub:

    implements(IPhysicallyLocatable)

    def __init__(self, obj):
        self.obj = obj

    def getRoot(self):
        return None

    def getPath(self):
        return str(id(self.obj))


class SQLScriptTest(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(SQLScriptTest, self).setUp()
        classImplements(SQLScript, IAttributeAnnotatable)
        self.connectionUtilityStub = ConnectionUtilityStub()
        ztapi.provideUtility(IZopeDatabaseAdapter, self.connectionUtilityStub,
                             'my_connection')
        
        ztapi.provideAdapter(IAttributeAnnotatable, IAnnotations,
                             AttributeAnnotations)
        ztapi.provideAdapter(ISQLScript, IPhysicallyLocatable,
                             LocatableStub)
        ztapi.provideAdapter(IAnnotatable, ICacheable,
                             AnnotationCacheable)

    def tearDown(self):
        pass
        
        #nextservice.getNextServiceManager = self._old_getNextServiceManager

    def _getScript(self):
        return SQLScript("my_connection",
                         "SELECT name, counter FROM Table WHERE"
                         " <dtml-sqltest id type=int>",
                         'id')

    def testGetArguments(self):
        assert isinstance(arguments, StringTypes), \
               '"arguments" argument of setArguments() must be a string'
        self._arg_string = arguments
        self.arguments = parseArguments(arguments)

    def testGetArguments(self):
        result = Arguments({'id': {}})
        args = self._getScript().getArguments()
        self.assertEqual(args, result)

    def testGetArgumentsString(self):
        self.assertEqual('id', self._getScript().getArgumentsString())

    def testSetSource(self):
        script = self._getScript()
        script.setSource('SELECT * FROM Table')
        self.assertEqual('SELECT * FROM Table', script.getSource())

    def testGetSource(self):
        expected = ("SELECT name, counter FROM Table"
                    " WHERE <dtml-sqltest id type=int>")
        self.assertEqual(expected,
                         self._getScript().getSource())

    def testConnectionName(self):
        script = self._getScript()
        self.assertEqual('my_connection', script.connectionName)
        script.connectionName = 'test_conn'
        self.assertEqual('test_conn', script.connectionName)

    def testgetConnection(self):
        script = self._getScript()
        name = script.connectionName
        conns = script.getConnection()
        self.assertEqual(conns, self.connectionUtilityStub.connection)

    def testSQLScript(self):
        result = self._getScript()(id=1)
        self.assertEqual(result.columns, ('name','counter'))
        self.assertEqual(result[0].name, 'stephan')

    def testSQLScriptCaching(self):
        script = self._getScript()
        CursorStub.count = 0
        # no caching: check that the counter grows
        result = script(id=1)
        self.assertEqual(result[0].counter, 1)
        result = script(id=1)
        self.assertEqual(result[0].counter, 2)
        # caching: and check that the counter stays still
        AnnotationCacheable(script).setCacheId('dumbcache')
        ztapi.provideUtility(ICache, CacheStub(), 'dumbcache')
        result = script(id=1)
        self.assertEqual(result[0].counter, 3)
        result = script(id=1)
        self.assertEqual(result[0].counter, 3)
        result = script(id=2)
        self.assertEqual(result[0].counter, 4)


def test_suite():
    return unittest.makeSuite(SQLScriptTest)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
