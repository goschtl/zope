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
"""Unit test for CacheConfiguration.

$Id: testCacheConfiguration.py,v 1.2 2002/12/18 17:39:09 stevea Exp $
"""

from unittest import TestCase, main, makeSuite

from Zope.App.OFS.Services.CachingService.CacheConfiguration \
     import CacheConfiguration

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.Traversing import traverse
from Zope.App.OFS.Services.ServiceManager.ServiceManager \
     import ServiceManager
from Zope.App.OFS.Container.ZopeContainerAdapter import ZopeContainerAdapter
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import Active, Unregistered
from Zope.App.Caching.ICache import ICache
from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.Caching.ICachingService import ICachingService
from Zope.App.OFS.Services.ConfigurationInterfaces import IConfigurable
from Zope.App.OFS.Services.Configuration import ConfigurationRegistry
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.ContextWrapper import ContextMethod
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Event.IObjectEvent import IObjectModifiedEvent


class DependableStub:

    __implements__ = IDependable

    def addDependent(self, location):
        pass

    def removeDependent(self, location):
        pass

    def dependents(self):
        pass


class TestCache(DependableStub):

    __implements__ = ICache, IDependable

    def invalidateAll(self):
        self.invalidated = True


class CachingServiceStub(DependableStub):

    __implements__ = ICachingService, IConfigurable, IDependable

    def __init__(self):
        self.bindings = {}
        self.subscriptions = {}

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

    def subscribe(self, obj, event):
        self.subscriptions.setdefault(obj, []).append(event)

    def unsubscribe(self, obj, event):
        self.subscriptions.setdefault(obj, []).remove(event)

    def listSubscriptions(self, obj):
        return self.subscriptions.get(obj, [])


class TestConnectionConfiguration(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())

        self.default = traverse(self.rootFolder,
                           '++etc++Services/Packages/default')
        self.default.setObject('cch', TestCache())
        self.cch = traverse(self.default, 'cch')

        self.cm = ZopeContainerAdapter(traverse(self.default, "configure"))
        self.cm.setObject('', CacheConfiguration('cache_name',
                            '/++etc++Services/Packages/default/cch'))
        self.config = traverse(self.default, 'configure/1')

        self.default.setObject('cache_srv', CachingServiceStub())
        self.service = traverse(self.default, 'cache_srv')

        self.cm.setObject('', ServiceConfiguration('Caching',
                            '/++etc++Services/Packages/default/cache_srv'))
        traverse(self.default, 'configure/2').status = Active

    def tearDown(self):
        PlacefulSetup.tearDown(self)

    def test_getComponent(self):
        # This should be already tested by ComponentConfiguration tests, but
        # let's doublecheck
        self.assertEqual(self.config.getComponent(), self.cch)

    def test_status(self):
        self.assertEqual(self.config.status, Unregistered)
        self.config.status = Active
        self.assertEqual(self.config.status, Active)
        cr = self.service.queryConfigurations('cache_name')
        self.assertEqual(cr.active(), self.config)

    def test_activated(self):
        self.config.activated()
        self.assertEqual(self.service.listSubscriptions(self.cch),
                         [IObjectModifiedEvent])

    def test_deactivated(self):
        self.service.subscribe(self.cch, IObjectModifiedEvent)
        self.cch.invalidated = False
        self.config.deactivated()
        self.assertEqual(self.service.listSubscriptions(self.cch), [])
        self.failIf(not self.cch.invalidated,
                    "deactivation should call invalidateAll")


def test_suite():
    return makeSuite(TestConnectionConfiguration)


if __name__=='__main__':
    main(defaultTest='test_suite')

