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

$Id: test_connectionconfiguration.py,v 1.14 2003/06/05 12:03:18 stevea Exp $
"""
__metaclass__ = type

from unittest import TestCase, main, makeSuite
from zope.app.services.connection import ConnectionConfiguration
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.app.interfaces.services.configuration import Active, Unregistered
from zope.app.interfaces.rdb import IZopeDatabaseAdapter
from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.rdb import IConnectionService
from zope.app.interfaces.services.configuration import IConfigurable
from zope.app.services.configuration import ConfigurationRegistry
from zope.context import ContextMethod
from zope.app.context import ContextWrapper
from zope.app.interfaces.services.configuration \
     import IAttributeUseConfigurable, IUseConfiguration
from zope.app.tests import setup
from zope.app.interfaces.services.service import ILocalService
from zope.interface import implements

class DependableStub:

    implements(IDependable)

    def addDependent(self, location):
        pass

    def removeDependent(self, location):
        pass

    def dependents(self):
        pass


class TestDA(DependableStub):

    implements(IZopeDatabaseAdapter, IDependable, IUseConfiguration)

    def addUsage(self, location):
        pass


class ConnectionServiceStub(DependableStub):

    implements(IConnectionService, IConfigurable, IDependable,
               IAttributeUseConfigurable, ILocalService)

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
        sm = PlacefulSetup.setUp(self, site=True)
        self.service = setup.addService(sm, 'SQLDatabaseConnections',
                                        ConnectionServiceStub())

        self.default = traverse(self.rootFolder,
                           '++etc++site/default')
        self.default.setObject('da', TestDA())
        self.da = traverse(self.default, 'da')

        self.cm = self.default.getConfigurationManager()
        key = self.cm.setObject('',
                  ConnectionConfiguration('conn_name',
                                          '/++etc++site/default/da'))
        self.config = traverse(self.default.getConfigurationManager(), key)

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
