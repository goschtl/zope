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
"""Unit tests for registration classes

$Id: test_registrations.py,v 1.1 2003/06/21 21:22:13 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface import Interface, implements
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.dependable import DependencyError
from zope.app.services.registration import SimpleRegistration
from zope.app.services.registration import ComponentRegistration
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


class TestSimpleRegistration(TestCase):

    def test_beforeDeleteHook(self):
        container = object()
        cfg = SimpleRegistration()

        # cannot delete an active registration
        cfg.status = ActiveStatus
        self.assertRaises(DependencyError, cfg.beforeDeleteHook, cfg,
                          container)

        # deletion of a registered registration causes it to become
        # unregistered
        cfg.status = RegisteredStatus
        cfg.beforeDeleteHook(cfg, container)
        self.assertEquals(cfg.status, UnregisteredStatus)


class TestComponentRegistration(TestSimpleRegistration, PlacefulSetup):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        self.name = 'foo'

    def test_getComponent(self):
        # set up a component
        name, component = 'foo', object()
        self.rootFolder.setObject(name, component)
        # set up a registration
        cfg = ComponentRegistration("/"+name)
        cfg = ContextWrapper(cfg, self.rootFolder)
        # check that getComponent finds the registration
        self.assertEquals(cfg.getComponent(), component)

    def test_getComponent_permission(self):
        # set up a component
        name, component = 'foo', object()
        self.rootFolder.setObject(name, component)
        # set up a registration
        cfg = ComponentRegistration("/"+name, 'zope.TopSecret')
        cfg.getInterface = lambda: ITestComponent
        cfg = ContextWrapper(cfg, self.rootFolder)
        # check that getComponent finds the registration
        result = cfg.getComponent()
        self.assertEquals(result, component)
        self.failUnless(type(result) is Proxy)

    def test_afterAddHook(self):
        # set up a component
        name, component = 'foo', ComponentStub()
        self.rootFolder.setObject(name, component)
        # set up a registration
        cfg = ComponentRegistration("/"+name)
        self.rootFolder.setObject('cfg', cfg)
        cfg = traverse(self.rootFolder, 'cfg')
        # simulate IAddNotifiable
        cfg.afterAddHook(cfg, self.rootFolder)
        # check that the dependency tracking works
        self.assertEquals(component.dependents(), ('/cfg',))

    def test_beforeDeleteHook_dependents(self):
        # set up a component
        name, component = 'foo', ComponentStub()
        self.rootFolder.setObject(name, component)
        component.addDependent('/cfg')
        # set up a registration
        cfg = ComponentRegistration("/"+name)
        cfg.status = UnregisteredStatus
        self.rootFolder.setObject('cfg', cfg)
        cfg = traverse(self.rootFolder, 'cfg')
        # simulate IDeleteNotifiable
        cfg.beforeDeleteHook(cfg, self.rootFolder)
        # check that the dependency tracking works
        self.assertEquals(component.dependents(), ())


# NamedRegistration is too simple to need testing at the moment


def test_suite():
    return TestSuite((
        makeSuite(TestSimpleRegistration),
        makeSuite(TestComponentRegistration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
