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

$Id: test_registrations.py,v 1.1 2004/03/13 18:01:18 srichter Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface import Interface, implements
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.interfaces.dependable import DependencyError
from zope.app.registration.registration import \
     SimpleRegistration, ComponentRegistration
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.interfaces.dependable import IDependable
from zope.app.traversing import traverse
from zope.security.proxy import Proxy
from zope.app.container.contained import ObjectRemovedEvent

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

    def setUp(self):
        # We can't use the status property on a SimpleRegistration instance.
        # we disable it for these tests
        self.__oldprop = SimpleRegistration.status
        del SimpleRegistration.status

    def tearDown(self):
        # Restore the status prop
        SimpleRegistration.status = self.__oldprop

    def test_removeNotify(self):
        cfg = SimpleRegistration()

        # cannot delete an active registration
        cfg.status = ActiveStatus
        event = ObjectRemovedEvent(cfg, None, 'somename')
        self.assertRaises(DependencyError, cfg.removeNotify, event)

        # deletion of a registered registration causes it to become
        # unregistered
        cfg.status = RegisteredStatus
        cfg.removeNotify(event)
        self.assertEquals(cfg.status, UnregisteredStatus)


class TestComponentRegistration(TestSimpleRegistration, PlacefulSetup):

    def setUp(self):
        TestSimpleRegistration.setUp(self)
        PlacefulSetup.setUp(self, site=True)
        self.name = 'foo'

    def test_getComponent(self):
        # set up a component
        name, component = 'foo', object()
        self.rootFolder[name] = component
        # set up a registration
        cfg = ComponentRegistration("/"+name)
        cfg.__parent__ = self.rootFolder
        # check that getComponent finds the registration
        self.assertEquals(cfg.getComponent(), component)

    def test_getComponent_permission(self):
        # set up a component
        name, component = 'foo', object()
        self.rootFolder[name] = component
        # set up a registration
        cfg = ComponentRegistration("/"+name, 'zope.TopSecret')
        cfg.getInterface = lambda: ITestComponent
        cfg.__parent__ = self.rootFolder
        # check that getComponent finds the registration
        result = cfg.getComponent()
        self.assertEquals(result, component)
        self.failUnless(type(result) is Proxy)

    def test_addNotify(self):
        # set up a component
        name, component = 'foo', ComponentStub()
        self.rootFolder[name] = component
        # set up a registration
        cfg = ComponentRegistration("/"+name)
        self.rootFolder['cfg'] = cfg
        cfg = traverse(self.rootFolder, 'cfg')
        # check that the dependency tracking works
        self.assertEquals(component.dependents(), ('/cfg',))

    def test_removeNotify_dependents(self):
        # set up a component
        name, component = 'foo', ComponentStub()
        self.rootFolder[name] = component
        component.addDependent('/cfg')
        # set up a registration
        cfg = ComponentRegistration("/"+name)
        cfg.status = UnregisteredStatus
        self.rootFolder['cfg'] = cfg
        cfg = traverse(self.rootFolder, 'cfg')
        # simulate IRemoveNotifiable
        event = ObjectRemovedEvent(cfg, self.rootFolder, 'cfg')
        cfg.removeNotify(event)
        # check that the dependency tracking works
        self.assertEquals(component.dependents(), ())

def test_suite():
    return TestSuite((
        makeSuite(TestSimpleRegistration),
        makeSuite(TestComponentRegistration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
