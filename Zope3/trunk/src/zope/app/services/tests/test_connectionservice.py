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

$Id: test_connectionservice.py,v 1.6 2003/03/23 22:35:42 jim Exp $
"""

import unittest
from zope.app.traversing import traverse
from zope.app.interfaces.rdb import IZopeConnection
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.rdb import \
     IConnectionService
from zope.app.container.zopecontainer import ZopeContainerAdapter
from zope.app.services.connection import \
     ConnectionService
from zope.app.services.service \
     import ServiceManager
from zope.app.services.service \
     import ServiceConfiguration
from zope.app.interfaces.dependable import IDependable
from zope.app.services.tests.placefulsetup \
     import PlacefulSetup
from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.attributeannotations import AttributeAnnotations
from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.dependable import IDependable
from zope.app.dependable import Dependable
from zope.component.adapter import provideAdapter
from zope.app.interfaces.services.configuration \
     import Active, Unregistered, Registered
from zope.app.services.connection \
     import ConnectionConfiguration
from zope.app.interfaces.services.configuration import IAttributeUseConfigurable


class ConnectionServiceForTests(ConnectionService):

    __implements__ = ConnectionService.__implements__, IAttributeUseConfigurable

class DAStub:

    __implements__ = IZopeDatabaseAdapter, IAttributeAnnotatable

    def __init__(self, n):
        self.n = n

    def __call__(self):
        return 'DA #%d' % self.n


def sort(list):
    list.sort()
    return list


class TestConnectionService(unittest.TestCase, PlacefulSetup):

    def setUp(self):
        PlacefulSetup.setUp(self)

        provideAdapter(IAttributeAnnotatable,
                       IAnnotations, AttributeAnnotations)
        provideAdapter(IAnnotatable, IDependable, Dependable)

        # Set up a local connection service
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())

        self.default = traverse(self.rootFolder,
                                '++etc++site/default')
        self.default.setObject('conn_srv', ConnectionServiceForTests())
        self.service = traverse(self.default, 'conn_srv')

        self.cm = ZopeContainerAdapter(self.default.getConfigurationManager())
        self.cm.setObject('', ServiceConfiguration('SQLDatabaseConnections',
                                '/++etc++site/default/conn_srv'))
        traverse(self.default.getConfigurationManager(), '1').status = Active

        self.default.setObject('da1', DAStub(1))
        self.default.setObject('da2', DAStub(2))

        self.cm.setObject('', ConnectionConfiguration('conn1',
                                '/++etc++site/default/da1'))
        traverse(self.default.getConfigurationManager(), '2').status = Active
        self.cm.setObject('', ConnectionConfiguration('conn2',
                                '/++etc++site/default/da2'))
        traverse(self.default.getConfigurationManager(), '3').status = Active
        self.cm.setObject('', ConnectionConfiguration('conn3',
                                '/++etc++site/default/da1'))
        traverse(self.default.getConfigurationManager(), '4').status = Registered
        # Now self.service has conn1 and conn2 available and knows about conn3

        # Set up a more local connection service
        folder1 = traverse(self.rootFolder, 'folder1')
        folder1.setServiceManager(ServiceManager())

        default1 = traverse(folder1, '++etc++site/default')
        default1.setObject('conn_srv1', ConnectionServiceForTests())
        self.service1 = traverse(default1, 'conn_srv1')

        cm1 = ZopeContainerAdapter(default1.getConfigurationManager())
        cm1.setObject('', ServiceConfiguration('SQLDatabaseConnections',
                '/folder1/++etc++site/default/conn_srv1'))
        traverse(default1.getConfigurationManager(), '1').status = Active

        default1.setObject('da3', DAStub(3))
        default1.setObject('da4', DAStub(4))

        cm1.setObject('', ConnectionConfiguration('conn1',
                            '/folder1/++etc++site/default/da3'))
        traverse(default1.getConfigurationManager(), '2').status = Active
        cm1.setObject('', ConnectionConfiguration('conn4',
                            '/folder1/++etc++site/default/da4'))
        traverse(default1.getConfigurationManager(), '3').status = Active
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
