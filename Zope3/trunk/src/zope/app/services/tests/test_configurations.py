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
"""Unit tests for configuration classes

$Id: test_configurations.py,v 1.2 2002/12/25 14:13:20 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface import Interface
from zope.app.interfaces.services.configuration \
        import Active, Registered, Unregistered
from zope.app.interfaces.dependable import DependencyError
from zope.app.services.configuration import SimpleConfiguration
from zope.app.services.configuration import NamedComponentConfiguration
from zope.app.services.tests.placefulsetup \
        import PlacefulSetup
from zope.app.services.tests.servicemanager \
        import TestingServiceManager
from zope.proxy.context import ContextWrapper
from zope.app.interfaces.dependable import IDependable
from zope.app.traversing import traverse
from zope.security.proxy import Proxy


class ITestComponent(Interface):
    pass

class ComponentStub:

    __implements__ = IDependable

    _dependents = ()

    def addDependent(self, location):
        self._dependents = tuple(
            [d for d in self._dependents if d != location]
            +
            [location]
            )

    def removeDependent(self, location):
        self._dependents = tuple(
            [d for d in self._dependents if d != location]
            )

    def dependents(self):
        return self._dependents



class TestSimpleConfiguration(TestCase):

    def test_manage_beforeDelete(self):
        container = object()
        cfg = SimpleConfiguration()

        # cannot delete an active configuration
        cfg.status = Active
        self.assertRaises(DependencyError, cfg.manage_beforeDelete, cfg,
                          container)

        # deletion of a registered configuration causes it to become
        # unregistered
        cfg.status = Registered
        cfg.manage_beforeDelete(cfg, container)
        self.assertEquals(cfg.status, Unregistered)


class TestNamedComponentConfiguration(TestSimpleConfiguration, PlacefulSetup):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.__sm = TestingServiceManager()
        self.rootFolder.setServiceManager(self.__sm)
        self.name = 'foo'

    def test_getComponent(self):
        # set up a component
        path, component = 'foo', object()
        self.rootFolder.setObject(path, component)
        # set up a configuration
        cfg = NamedComponentConfiguration(self.name, path)
        cfg = ContextWrapper(cfg, self.rootFolder)
        # check that getComponent finds the configuration
        self.assertEquals(cfg.getComponent(), component)

    def test_getComponent_permission(self):
        # set up a component
        path, component = 'foo', object()
        self.rootFolder.setObject(path, component)
        # set up a configuration
        cfg = NamedComponentConfiguration(self.name, path, 'zope.TopSecret')
        cfg.getInterface = lambda: ITestComponent
        cfg = ContextWrapper(cfg, self.rootFolder)
        # check that getComponent finds the configuration
        result = cfg.getComponent()
        self.assertEquals(result, component)
        self.failUnless(type(result) is Proxy)

    def test_manage_afterAdd(self):
        # set up a component
        path, component = 'foo', ComponentStub()
        self.rootFolder.setObject(path, component)
        # set up a configuration
        cfg = NamedComponentConfiguration(self.name, path)
        self.rootFolder.setObject('cfg', cfg)
        cfg = traverse(self.rootFolder, 'cfg')
        # simulate IAddNotifiable
        cfg.manage_afterAdd(cfg, self.rootFolder)
        # check that the dependency tracking works
        self.assertEquals(component.dependents(), ('/cfg',))

    def test_manage_beforeDelete_dependents(self):
        # set up a component
        path, component = 'foo', ComponentStub()
        self.rootFolder.setObject(path, component)
        component.addDependent('/cfg')
        # set up a configuration
        cfg = NamedComponentConfiguration(self.name, path)
        cfg.status = Unregistered
        self.rootFolder.setObject('cfg', cfg)
        cfg = traverse(self.rootFolder, 'cfg')
        # simulate IDeleteNotifiable
        cfg.manage_beforeDelete(cfg, self.rootFolder)
        # check that the dependency tracking works
        self.assertEquals(component.dependents(), ())


# NamedConfiguration is too simple to need testing at the moment


def test_suite():
    return TestSuite((
        makeSuite(TestSimpleConfiguration),
        makeSuite(TestNamedComponentConfiguration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
