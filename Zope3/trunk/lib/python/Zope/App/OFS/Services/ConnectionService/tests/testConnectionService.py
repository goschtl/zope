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

$Id: testConnectionService.py,v 1.5 2002/12/09 15:26:42 ryzaja Exp $
"""

import unittest
from Zope.ComponentArchitecture.GlobalServiceManager import \
     serviceManager as sm
from Zope.App.Traversing import traverse
from Zope.App.RDB.IZopeConnection import IZopeConnection
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter
from Zope.App.RDB.IConnectionService import \
     IConnectionService
from Zope.App.OFS.Container.ZopeContainerAdapter import ZopeContainerAdapter
from Zope.App.OFS.Services.ConnectionService.ConnectionService import \
     ConnectionService
from Zope.App.OFS.Services.ServiceManager.ServiceManager \
     import ServiceManager
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.OFS.Annotation.IAnnotatable import IAnnotatable
from Zope.App.OFS.Annotation.IAttributeAnnotatable import IAttributeAnnotatable
from Zope.App.OFS.Annotation.AttributeAnnotations import AttributeAnnotations
from Zope.App.OFS.Annotation.IAnnotations import IAnnotations
from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.DependencyFramework.Dependable import Dependable
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import Active, Unregistered, Registered
from Zope.App.OFS.Services.ConnectionService.ConnectionConfiguration \
     import ConnectionConfiguration


class DAStub:

    __implements__ = IZopeDatabaseAdapter, IAttributeAnnotatable

    def __call__(self):
        return 'Connection'


def sort(list):
    list.sort()
    return list


class TestConnectionService(unittest.TestCase, PlacefulSetup):

    def setUp(self):
        PlacefulSetup.setUp(self)

        provideAdapter(IAttributeAnnotatable,
                       IAnnotations, AttributeAnnotations)
        provideAdapter(IAnnotatable, IDependable, Dependable)

        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        sm = self.rootFolder.getServiceManager()

        self.default = traverse(self.rootFolder,
                           '++etc++Services/Packages/default')
        self.default.setObject('conn_srv', ConnectionService())
        self.service = traverse(self.default, 'conn_srv')

        self.cm = ZopeContainerAdapter(traverse(self.default, "configure"))
        self.cm.setObject('', ServiceConfiguration('SQLDatabaseConnections',
                            '/++etc++Services/Packages/default/conn_srv'))
        traverse(self.default, 'configure/1').status = Active

        self.default.setObject('da1', DAStub())
        self.default.setObject('da2', DAStub())

        self.cm.setObject('', ConnectionConfiguration('conn1',
                            '/++etc++Services/Packages/default/da1'))
        traverse(self.default, 'configure/2').status = Active
        self.cm.setObject('', ConnectionConfiguration('conn2',
                            '/++etc++Services/Packages/default/da2'))
        traverse(self.default, 'configure/3').status = Active

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


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConnectionService))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
