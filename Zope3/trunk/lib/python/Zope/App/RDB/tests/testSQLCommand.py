##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
$Id: testSQLCommand.py,v 1.5 2002/10/04 18:37:24 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Zope.App.RDB.SQLCommand import SQLCommand
from Zope.App.RDB.IConnectionService import IConnectionService
from Zope.App.RDB.IZopeConnection import IZopeConnection
from Zope.App.RDB.IZopeCursor import IZopeCursor
from Zope.App.ComponentArchitecture import NextService
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalServiceManager import \
     serviceManager as sm


# Make spme fixes, so that we overcome some of the natural ZODB properties
def getNextServiceManager(context):
    return sm

class CursorStub:

    __implements__ = IZopeCursor

    description = (('id', 'int'),)

    def execute(self, operation, parameters=None):
        self.result = {"SELECT id FROM Table": ((1,),)}[operation]

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


class Test(TestCase, PlacelessSetup):


    def setUp(self):
        PlacelessSetup.setUp(self)
        sm.defineService('Connections', IConnectionService)
        sm.provideService('Connections', ConnectionServiceStub())
        self._old_getNextServiceManager = NextService.getNextServiceManager
        NextService.getNextServiceManager = getNextServiceManager

    def tearDown(self):
        NextService.getNextServiceManager = self._old_getNextServiceManager


    def testSimpleSQLCommand(self):
        command = SQLCommand("my_connection", "SELECT id FROM Table")
        result = command()
        self.assertEqual(result.names, ('id',))
        self.assertEqual(result[0].id, 1)


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')



