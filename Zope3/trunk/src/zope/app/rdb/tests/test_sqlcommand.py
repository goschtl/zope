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
$Id: test_sqlcommand.py,v 1.3 2003/03/03 23:16:11 gvanrossum Exp $
"""

import unittest

from zope.app.component import nextservice
from zope.app.interfaces.rdb import IConnectionService
from zope.app.interfaces.rdb import IZopeConnection
from zope.app.interfaces.rdb import IZopeCursor
from zope.app.rdb import SQLCommand
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component.service import serviceManager as sm
from zope.app.interfaces.services.interfaces import ISimpleService


# Make some fixes, so that we overcome some of the natural ZODB properties
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

    __implements__ = IConnectionService, ISimpleService

    def getConnection(self, name):
        return ConnectionStub()


class SQLCommandTest(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)
        sm.defineService('SQLDatabaseConnections', IConnectionService)
        sm.provideService('SQLDatabaseConnections', ConnectionServiceStub())
        self._old_getNextServiceManager = nextservice.getNextServiceManager
        nextservice.getNextServiceManager = getNextServiceManager

    def tearDown(self):
        nextservice.getNextServiceManager = self._old_getNextServiceManager

    def testsimp(self):
        command = SQLCommand("my_connection", "SELECT id FROM Table")
        result = command()
        self.assertEqual(result.columns, ('id',))
        self.assertEqual(result[0].id, 1)


def test_suite():
    return unittest.makeSuite(SQLCommandTest)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
