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

$Id: testSQLScript.py,v 1.1 2002/07/11 00:03:19 srichter Exp $
"""

import unittest

from Zope.App.RDB.IConnectionService import IConnectionService
from Zope.App.RDB.IZopeConnection import IZopeConnection
from Zope.App.RDB.IZopeCursor import IZopeCursor
import Zope.ComponentArchitecture
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalServiceManager import \
     serviceManager as sm

from Zope.App.OFS.Content.SQLScript.SQLScript import SQLScript 
from Zope.App.OFS.Content.SQLScript.Arguments import Arguments

# Make spme fixes, so that we overcome some of the natural ZODB properties
def getNextServiceManager(context):
    return sm

class CursorStub:

    __implements__ = IZopeCursor

    description = (('name', 'string'),)

    def execute(self, operation, parameters=None):
        self.result = {"SELECT name FROM Table WHERE id = 1":
                       (('stephan',),)}[operation]

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


class SQLScriptTest(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)
        sm.defineService('ConnectionService', IConnectionService)
        sm.provideService('ConnectionService', ConnectionServiceStub())
        self._old_getNextServiceManager = \
                              Zope.ComponentArchitecture.getNextServiceManager
        Zope.ComponentArchitecture.getNextServiceManager = \
                              getNextServiceManager

    def tearDown(self):
        Zope.ComponentArchitecture.getNextServiceManager = \
                              self._old_getNextServiceManager
        

    def _getScript(self):
        return SQLScript("my_connection",
                   "SELECT name FROM Table WHERE <dtml-sqltest id type=int>",
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
            "SELECT name FROM Table WHERE <dtml-sqltest id type=int>",
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
        self.assertEqual(result.names, ('name',))
        self.assertEqual(result[0].name, 'stephan')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SQLScriptTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
