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

$Id: test_connectionconfiguration.py,v 1.2 2002/12/25 14:13:20 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface import Interface

from zope.app.services.connection import ConnectionConfiguration

from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.app.services.service import ServiceManager
from zope.app.container.zopecontainer import ZopeContainerAdapter
from zope.app.interfaces.services.configuration import Active, Unregistered
from zope.app.interfaces.services.configuration import Registered
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.rdb import IConnectionService
from zope.app.interfaces.services.configuration import IConfigurable
from zope.app.services.configuration import ConfigurationRegistry
from zope.app.services.service import ServiceConfiguration
from zope.proxy.context import ContextMethod
from zope.proxy.context import ContextWrapper

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
        return self.queryConfigurations(cfg.name)
    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(self, name, default=None):
        registry = self.bindings.get(name, default)
        return ContextWrapper(registry, self)
    queryConfigurations = ContextMethod(queryConfigurations)

    def createConfigurationsFor(self, cfg):
        return self.createConfigurations(cfg.name)
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
        # This should be already tested by ComponentConfiguration tests, but
        # let's doublecheck
        self.assertEqual(self.config.getComponent(), self.da)

    def test_status(self):
        self.assertEqual(self.config.status, Unregistered)
        self.config.status = Active
        self.assertEqual(self.config.status, Active)
        cr = self.service.queryConfigurations('conn_name')
        self.assertEqual(cr.active(), self.config)


def test_suite():
    return makeSuite(TestConnectionConfiguration)


if __name__=='__main__':
    main(defaultTest='test_suite')
