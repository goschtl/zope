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

$Id: test_connectionservice.py,v 1.11 2003/06/05 12:03:18 stevea Exp $
"""

import unittest

from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.services.configuration import Active, Registered
from zope.app.interfaces.services.configuration \
     import IAttributeUseConfigurable
from zope.app.services.connection import ConnectionConfiguration
from zope.app.services.connection import ConnectionService
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.tests import setup
from zope.app import zapi
from zope.interface import implements

class ConnectionServiceForTests(ConnectionService):

    implements(IAttributeUseConfigurable)

class DAStub:

    implements(IZopeDatabaseAdapter, IAttributeAnnotatable)

    def __init__(self, n):
        self.n = n

    def __call__(self):
        return 'DA #%d' % self.n


def sort(list):
    list.sort()
    return list


class TestConnectionService(unittest.TestCase, PlacefulSetup):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)
        self.service = setup.addService(sm, 'SQLDatabaseConnections',
                                        ConnectionServiceForTests())
        self.default = zapi.traverse(sm, 'default')

        self.default.setObject('da1', DAStub(1))
        self.default.setObject('da2', DAStub(2))

        self.cm = self.default.getConfigurationManager()

        k = self.cm.setObject('', ConnectionConfiguration('conn1',
                                '/++etc++site/default/da1'))
        zapi.traverse(self.default.getConfigurationManager(), k).status = Active
        k = self.cm.setObject('', ConnectionConfiguration('conn2',
                                '/++etc++site/default/da2'))
        zapi.traverse(self.default.getConfigurationManager(), k).status = Active
        k = self.cm.setObject('', ConnectionConfiguration('conn3',
                                '/++etc++site/default/da1'))
        zapi.traverse(self.default.getConfigurationManager(),
                 k).status = Registered
        # Now self.service has conn1 and conn2 available and knows about conn3

        sm = self.makeSite('folder1')
        self.service1 = setup.addService(sm, 'SQLDatabaseConnections',
                                         ConnectionServiceForTests())

        default1 = zapi.traverse(sm, 'default')
        default1.setObject('da3', DAStub(3))
        default1.setObject('da4', DAStub(4))

        cm1 = default1.getConfigurationManager()

        k = cm1.setObject('', ConnectionConfiguration('conn1',
                            '/folder1/++etc++site/default/da3'))
        zapi.traverse(default1.getConfigurationManager(), k).status = Active
        k = cm1.setObject('', ConnectionConfiguration('conn4',
                            '/folder1/++etc++site/default/da4'))
        zapi.traverse(default1.getConfigurationManager(), k).status = Active
        # Now self.service1 overrides conn1, adds new conn4 available, and
        # inherits conn2 from self.service

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
