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

$Id: test_connectionservice.py,v 1.15 2003/09/21 17:33:13 jim Exp $
"""

import unittest

from zope.app import zapi
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.services.connection import ILocalConnectionService
from zope.app.interfaces.services.registration import \
     ActiveStatus, RegisteredStatus
from zope.app.interfaces.services.utility import ILocalUtility
from zope.app.services.connection import ConnectionService
from zope.app.services.servicenames import SQLDatabaseConnections, Utilities
from zope.app.services.utility import LocalUtilityService, UtilityRegistration
from zope.app.tests import setup
from zope.component import getServiceManager
from zope.interface import implements

class DAStub:

    implements(IZopeDatabaseAdapter, IAttributeAnnotatable)

    def __init__(self, n):
        self.n = n

    def __call__(self):
        return 'DA #%d' % self.n


def sort(list):
    list.sort()
    return list


def addConnection(servicemanager, name, connection, status=ActiveStatus):
    """Add a menu to the service manager's default package."""
    default = zapi.traverse(servicemanager, 'default')
    default[name] = connection
    path = "%s/default/%s" % (zapi.getPath(servicemanager), name)
    registration = UtilityRegistration(name, IZopeDatabaseAdapter, path)
    key = default.getRegistrationManager().addRegistration(registration)
    zapi.traverse(default.getRegistrationManager(), key).status = status
    return zapi.traverse(default, name)    


class TestConnectionService(unittest.TestCase):

    def setUp(self):
        setup.placefulSetUp()
        self.rootFolder = setup.buildSampleFolderTree()

        # Define Connection Service
        sm=getServiceManager(None)
        sm.defineService(SQLDatabaseConnections, ILocalConnectionService)

        # Create Components in root folder
        mgr = setup.createServiceManager(self.rootFolder)
        setup.addService(mgr, Utilities, LocalUtilityService())

        self.service = setup.addService(mgr, SQLDatabaseConnections,
                                        ConnectionService())

        conn = addConnection(mgr, 'conn1', DAStub(1))
        conn = addConnection(mgr, 'conn2', DAStub(2))
        conn = addConnection(mgr, 'conn3', DAStub(3), RegisteredStatus)

        mgr = setup.createServiceManager(
            zapi.traverse(self.rootFolder, 'folder1'))
        setup.addService(mgr, Utilities, LocalUtilityService())

        self.service1 = setup.addService(mgr, SQLDatabaseConnections,
                                         ConnectionService())

        conn = addConnection(mgr, 'conn1', DAStub(3))
        conn = addConnection(mgr, 'conn4', DAStub(4))

    def testGetConnection(self):
        self.assertEqual('DA #1', self.service.getConnection('conn1'))
        self.assertEqual('DA #2', self.service.getConnection('conn2'))
        self.assertRaises(KeyError, self.service.getConnection, 'conn3')
        self.assertRaises(KeyError, self.service.getConnection, 'conn4')

        self.assertEqual('DA #3', self.service1.getConnection('conn1'))
        self.assertEqual('DA #2', self.service1.getConnection('conn2'))
        self.assertRaises(KeyError, self.service1.getConnection, 'conn3')
        self.assertEqual('DA #4', self.service1.getConnection('conn4'))
        self.assertRaises(KeyError, self.service1.getConnection, 'conn5')

    def testQueryConnection(self):
        self.assertEqual('DA #1', self.service.queryConnection('conn1'))
        self.assertEqual('DA #2', self.service.queryConnection('conn2'))
        self.assertEqual(None, self.service.queryConnection('conn3'))
        self.assertEqual('xx', self.service.queryConnection('conn3', 'xx'))
        self.assertEqual(None, self.service.queryConnection('conn4'))
        self.assertEqual('xx', self.service.queryConnection('conn4', 'xx'))

        self.assertEqual('DA #3', self.service1.queryConnection('conn1'))
        self.assertEqual('DA #2', self.service1.queryConnection('conn2'))
        self.assertEqual(None, self.service1.queryConnection('conn3'))
        self.assertEqual('xx', self.service1.queryConnection('conn3', 'xx'))
        self.assertEqual('DA #4', self.service1.queryConnection('conn4'))
        self.assertEqual(None, self.service1.queryConnection('conn5'))
        self.assertEqual('xx', self.service1.queryConnection('conn5', 'xx'))

    def testGetAvailableConnections(self):
        self.assertEqual(['conn1', 'conn2'],
                         sort(self.service.getAvailableConnections()))
        self.assertEqual(['conn1', 'conn2', 'conn4'],
                         sort(self.service1.getAvailableConnections()))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConnectionService))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
