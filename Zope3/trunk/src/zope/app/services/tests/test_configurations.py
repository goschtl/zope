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

$Id: test_configurations.py,v 1.8 2003/06/07 05:32:01 stevea Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface import Interface, implements
from zope.app.interfaces.services.configuration \
        import Active, Registered, Unregistered
from zope.app.interfaces.dependable import DependencyError
from zope.app.services.configuration import SimpleConfiguration
from zope.app.services.configuration import ComponentConfiguration
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.context import ContextWrapper
from zope.app.interfaces.dependable import IDependable
from zope.app.traversing import traverse
from zope.security.proxy import Proxy


class ITestComponent(Interface):
    pass

class ComponentStub:

    implements(IDependable)

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

    def test_beforeDeleteHook(self):
        container = object()
        cfg = SimpleConfiguration()

        # cannot delete an active configuration
        cfg.status = Active
        self.assertRaises(DependencyError, cfg.beforeDeleteHook, cfg,
                          container)

        # deletion of a registered configuration causes it to become
        # unregistered
        cfg.status = Registered
        cfg.beforeDeleteHook(cfg, container)
        self.assertEquals(cfg.status, Unregistered)


class TestComponentConfiguration(TestSimpleConfiguration, PlacefulSetup):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        self.name = 'foo'

    def test_getComponent(self):
        # set up a component
        path, component = 'foo', object()
        self.rootFolder.setObject(path, component)
        # set up a configuration
        cfg = ComponentConfiguration(path)
        cfg = ContextWrapper(cfg, self.rootFolder)
        # check that getComponent finds the configuration
        self.assertEquals(cfg.getComponent(), component)

    def test_getComponent_permission(self):
        # set up a component
        path, component = 'foo', object()
        self.rootFolder.setObject(path, component)
        # set up a configuration
        cfg = ComponentConfiguration(path, 'zope.TopSecret')
        cfg.getInterface = lambda: ITestComponent
        cfg = ContextWrapper(cfg, self.rootFolder)
        # check that getComponent finds the configuration
        result = cfg.getComponent()
        self.assertEquals(result, component)
        self.failUnless(type(result) is Proxy)

    def test_afterAddHook(self):
        # set up a component
        path, component = 'foo', ComponentStub()
        self.rootFolder.setObject(path, component)
        # set up a configuration
        cfg = ComponentConfiguration(path)
        self.rootFolder.setObject('cfg', cfg)
        cfg = traverse(self.rootFolder, 'cfg')
        # simulate IAddNotifiable
        cfg.afterAddHook(cfg, self.rootFolder)
        # check that the dependency tracking works
        self.assertEquals(component.dependents(), ('/cfg',))

    def test_beforeDeleteHook_dependents(self):
        # set up a component
        path, component = 'foo', ComponentStub()
        self.rootFolder.setObject(path, component)
        component.addDependent('/cfg')
        # set up a configuration
        cfg = ComponentConfiguration(path)
        cfg.status = Unregistered
        self.rootFolder.setObject('cfg', cfg)
        cfg = traverse(self.rootFolder, 'cfg')
        # simulate IDeleteNotifiable
        cfg.beforeDeleteHook(cfg, self.rootFolder)
        # check that the dependency tracking works
        self.assertEquals(component.dependents(), ())


# NamedConfiguration is too simple to need testing at the moment


def test_suite():
    return TestSuite((
        makeSuite(TestSimpleConfiguration),
        makeSuite(TestComponentConfiguration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
