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
"""Unit test for ConnectionConfiguration.

$Id: testConnectionConfiguration.py,v 1.1 2002/12/09 15:26:42 ryzaja Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Interface import Interface

from Zope.App.OFS.Services.ConnectionService.ConnectionConfiguration \
     import ConnectionConfiguration

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.Traversing import traverse
from Zope.App.OFS.Services.ServiceManager.ServiceManager \
     import ServiceManager
from Zope.App.OFS.Container.ZopeContainerAdapter import ZopeContainerAdapter
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import Active, Unregistered, Registered
from Zope.App.RDB.IZopeDatabaseAdapter import IZopeDatabaseAdapter
from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.RDB.IConnectionService import IConnectionService
from Zope.App.OFS.Services.ConfigurationInterfaces import IConfigurable
from Zope.App.OFS.Services.Configuration import ConfigurationRegistry
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import ContextWrapper

class DependableStub:

    __implements__ = IDependable

    def addDependent(self, location):
        pass

    def removeDependent(self, location):
        pass

    def dependents(self):
        pass


class TestDA(DependableStub):

    __implements__ = IZopeDatabaseAdapter, IDependable


class ConnectionServiceStub(DependableStub):

    __implements__ = IConnectionService, IConfigurable, IDependable

    def __init__(self):
        self.bindings = {}

    def queryConfigurationsFor(self, cfg, default=None):
        return self.queryConfigurations(cfg.connectionName)
    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(self, name, default=None):
        registry = self.bindings.get(name, default)
        return ContextWrapper(registry, self)
    queryConfigurations = ContextMethod(queryConfigurations)

    def createConfigurationsFor(self, cfg):
        return self.createConfigurations(cfg.connectionName)
    createConfigurationsFor = ContextMethod(createConfigurationsFor)

    def createConfigurations(self, name):
        try:
            registry = self.bindings[name]
        except KeyError:
            self.bindings[name] = registry = ConfigurationRegistry()
        return ContextWrapper(registry, self)
    createConfigurations = ContextMethod(createConfigurations)


class TestConnectionConfiguration(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        sm = self.rootFolder.getServiceManager()

        self.default = traverse(self.rootFolder,
                           '++etc++Services/Packages/default')
        self.default.setObject('da', TestDA())
        self.da = traverse(self.default, 'da')

        self.cm = ZopeContainerAdapter(traverse(self.default, "configure"))
        self.cm.setObject('', ConnectionConfiguration('conn_name',
                            '/++etc++Services/Packages/default/da'))
        self.config = traverse(self.default, 'configure/1')

        self.default.setObject('conn_srv', ConnectionServiceStub())
        self.service = traverse(self.default, 'conn_srv')

        self.cm.setObject('', ServiceConfiguration('SQLDatabaseConnections',
                            '/++etc++Services/Packages/default/conn_srv'))
        traverse(self.default, 'configure/2').status = Active

    def tearDown(self):
        PlacefulSetup.tearDown(self)

    def test_getComponent(self):
        self.assertEqual(self.config.getComponent(), self.da)

    def test_status(self):
        self.assertEqual(self.config.status, Unregistered)
        self.config.status = Active
        self.assertEqual(self.config.status, Active)
        cr = self.service.queryConfigurations('conn_name')
        self.assertEqual(cr.active(), self.config)

    # Unit tests for ComponentConfiguration should take care
    # of test_manage_afterAdd, test_manage_beforeDelete_and_unregistered,
    # test_disallow_delete_when_active


def test_suite():
    return makeSuite(TestConnectionConfiguration)


if __name__=='__main__':
    main(defaultTest='test_suite')
