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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testConfigurationStatusProperty.py,v 1.2 2002/11/30 18:35:55 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.ComponentArchitecture.IServiceService import IServiceService
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.OFS.Services.RoleService.RoleService import RoleService
from TestingConfigurationRegistry \
     import TestingConfigurationRegistry, TestingConfiguration
from Zope.App.OFS.Services.Configuration import ConfigurationStatusProperty
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import Active, Unregistered, Registered
from Zope.Proxy.ContextWrapper import ContextWrapper

class TestingConfiguration(TestingConfiguration):
    status = ConfigurationStatusProperty("Services")
    service_type = "Test"

class TestingConfigurationRegistry(TestingConfigurationRegistry):
    class_ = TestingConfiguration

class TestingServiceManager:

    __implements__ = IServiceService # I lied

    registry = None

    def getService(self, name):
        if name == "Services":
            return self
        raise ValueError("Wrong service name", name)

    def queryConfigurationsFor(self, configuration, default=None):
        if configuration.service_type != "Test":
            raise ValueError("Bad service type", configuration.service_type)
        return self.registry

    def createConfigurationsFor(self, configuration):
        if configuration.service_type != "Test":
            raise ValueError("Bad service type", configuration.service_type)
        self.registry = TestingConfigurationRegistry()
        return self.registry


class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.__sm = TestingServiceManager()
        self.rootFolder.setServiceManager(self.__sm)

    def test(self):

        configa = ContextWrapper(TestingConfiguration('a'), self.rootFolder)
        self.assertEqual(configa.status, Unregistered)

        configa.status = Registered
        self.assertEqual(self.__sm.registry._data, (None, 'a'))
        self.assertEqual(configa.status, Registered)

        configa.status = Active
        self.assertEqual(self.__sm.registry._data, ('a', ))
        self.assertEqual(configa.status, Active)

        configb = ContextWrapper(TestingConfiguration('b'), self.rootFolder)
        self.assertEqual(self.__sm.registry._data, ('a', ))
        self.assertEqual(configb.status, Unregistered)

        configb.status = Registered
        self.assertEqual(self.__sm.registry._data, ('a', 'b'))
        self.assertEqual(configb.status, Registered)

        configc = ContextWrapper(TestingConfiguration('c'), self.rootFolder)
        self.assertEqual(configc.status, Unregistered)
        self.assertEqual(self.__sm.registry._data, ('a', 'b'))

        configc.status = Registered
        self.assertEqual(self.__sm.registry._data, ('a', 'b', 'c'))
        self.assertEqual(configc.status, Registered)

        configc.status = Active
        self.assertEqual(self.__sm.registry._data, ('c', 'a', 'b'))
        self.assertEqual(configc.status, Active)

        configc.status = Unregistered
        self.assertEqual(self.__sm.registry._data, (None, 'a', 'b'))
        self.assertEqual(configc.status, Unregistered)
        self.assertEqual(configb.status, Registered)
        self.assertEqual(configa.status, Registered)

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
