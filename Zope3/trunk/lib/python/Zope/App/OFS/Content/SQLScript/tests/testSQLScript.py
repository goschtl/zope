##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors. All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""DT_SQLVar Tests

$Id: testSQLScript.py,v 1.6 2002/10/07 09:54:39 mgedmin Exp $
"""

import unittest

from Zope.App.RDB.IConnectionService import IConnectionService
from Zope.App.RDB.IZopeConnection import IZopeConnection
from Zope.App.RDB.IZopeCursor import IZopeCursor
from Zope.ComponentArchitecture import getService
from Zope.App.ComponentArchitecture import NextService
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalServiceManager import \
     serviceManager as sm

from Zope.App.OFS.Content.SQLScript.SQLScript import SQLScript
from Zope.App.OFS.Content.SQLScript.Arguments import Arguments

from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations

from Zope.App.Caching.ICacheable import ICacheable
from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.Caching.AnnotationCacheable import AnnotationCacheable

# Make spme fixes, so that we overcome some of the natural ZODB properties
def getNextServiceManager(context):
    return sm

class CursorStub:

    __implements__ = IZopeCursor

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
    __implements__ = IZopeConnection

    def cursor(self):
        return CursorStub()


class ConnectionServiceStub:
    __implements__ = IConnectionService

    def getConnection(self, name):
        return ConnectionStub()


class CacheStub:

    def __init__(self):
        self.cache = {}

    def set(self, data, obj, view_name="", keywords=None, mtime_func=None):
        if keywords:
            keywords = keywords.items()
            keywords.sort()
            keywords = tuple(keywords)
        self.cache[obj, view_name, keywords] = data

    def query(self, obj, view_name="", keywords=None, mtime_func=None, default=None):
        if keywords:
            keywords = keywords.items()
            keywords.sort()
            keywords = tuple(keywords)
        return self.cache.get((obj, view_name, keywords), default)


class CachingServiceStub:

    __implements__ = ICachingService

    def __init__(self):
        self.caches = {}

    def getCache(self, name):
        return self.caches[name]


class SQLScriptTest(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)
        sm.defineService('Connections', IConnectionService)
        sm.provideService('Connections', ConnectionServiceStub())
        self._old_getNextServiceManager = NextService.getNextServiceManager
        NextService.getNextServiceManager = getNextServiceManager
        self.caching_service = CachingServiceStub()
        sm.defineService('Caching', ICachingService)
        sm.provideService('Caching', self.caching_service)
        getService(None, "Adapters").provideAdapter(
            IAttributeAnnotatable, IAnnotations,
            AttributeAnnotations)
        getService(None, "Adapters").provideAdapter(
            IAnnotatable, ICacheable,
            AnnotationCacheable)

    def tearDown(self):
        NextService.getNextServiceManager = self._old_getNextServiceManager

    def _getScript(self):
        return SQLScript("my_connection",
                   "SELECT name, counter FROM Table WHERE <dtml-sqltest id type=int>",
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
        self.assertEqual(
            "SELECT name, counter FROM Table WHERE <dtml-sqltest id type=int>",
            self._getScript().getSource())


    def testSetConnectionName(self):
        script = self._getScript()
        script.setConnectionName('test_conn')
        self.assertEqual('test_conn', script.getConnectionName())


    def testGetConnectionName(self):
        self.assertEqual('my_connection',
                         self._getScript().getConnectionName())


    def testSQLScript(self):
        result = self._getScript()(id=1)
        self.assertEqual(result.names, ('name','counter'))
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
        self.caching_service.caches['dumbcache'] = CacheStub()
        result = script(id=1)
        self.assertEqual(result[0].counter, 3)
        result = script(id=1)
        self.assertEqual(result[0].counter, 3)
        result = script(id=2)
        self.assertEqual(result[0].counter, 4)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SQLScriptTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
