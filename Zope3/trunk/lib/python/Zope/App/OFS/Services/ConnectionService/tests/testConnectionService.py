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

$Id: testConnectionService.py,v 1.2 2002/07/16 23:41:15 jim Exp $
"""

import unittest
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture.GlobalServiceManager import \
     serviceManager as sm
from Zope.App.RDB.IZopeConnection import IZopeConnection
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter
from Zope.App.RDB.IConnectionService import \
     IConnectionService
from Zope.App.OFS.Services.ConnectionService.ConnectionService import \
     ConnectionService


class DAStub:
    """ """

    __implements__ = IZopeDatabaseAdapter

    def __call__(self):
        return 'Connection'


def sort(list):
    list.sort()
    return list


class TestConnectionService(unittest.TestCase, PlacelessSetup):

    def setUp(self):
        PlacelessSetup.setUp(self)
        self.service = ConnectionService()
        self.service.setObject('conn1', DAStub())
        self.service.setObject('conn2', DAStub())
        sm.defineService('Connections', IConnectionService)
        sm.provideService('Connections', self.service)

    def testGetConnection(self):
        self.assertEqual('Connection',
                         self.service.getConnection('conn1'))
        self.assertRaises(KeyError, self.service.getConnection, 'conn3')

    def testQueryConnection(self):
        self.assertEqual('Connection',
                         self.service.queryConnection('conn1'))
        self.assertEqual(None,
                         self.service.queryConnection('conn3'))
        self.assertEqual('Error',
                         self.service.queryConnection('conn3', 'Error'))
        
    def testGetAvailableConnections(self):
        self.assertEqual(['conn1', 'conn2'],
                         sort(self.service.getAvailableConnections()))

    def testIsAddable(self):
        self.assertEqual(1, self.service.isAddable(IZopeDatabaseAdapter))
        self.assertEqual(0, self.service.isAddable(IZopeConnection))
        

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConnectionService))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
