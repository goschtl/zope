##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests for registration classes

$Id$
"""

from unittest import TestCase, TestSuite, main, makeSuite
from doctest import DocTestSuite

from zope.interface import Interface, implements
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.dependable.interfaces import DependencyError
from zope.app.registration.registration import \
     SimpleRegistration, ComponentRegistration
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.dependable.interfaces import IDependable
from zope.app.traversing.api import traverse
from zope.security.proxy import Proxy
from zope.app.container.contained import Contained
from zope.app.container.contained import ObjectRemovedEvent
from zope.app.tests import ztapi
from zope.app.registration.interfaces import IRegistration
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.registration.registration import \
    SimpleRegistrationRemoveSubscriber, \
    ComponentRegistrationRemoveSubscriber, \
    ComponentRegistrationAddSubscriber
from zope.app.traversing.interfaces import IPhysicallyLocatable
import zope.interface

class ITestComponent(Interface):
    pass

class ComponentStub(Contained):

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


class DummyRegistration(ComponentStub):
    implements (IRegistration, IPhysicallyLocatable)

    def __init__(self):
        self.status = UnregisteredStatus
        
    def getPath(self):
        return 'dummy!'

    def getComponent(self):
        return self
    
class TestSimpleRegistrationEvents(TestCase):

    def test_RemoveSubscriber(self):    
        reg = DummyRegistration()
        reg.status = ActiveStatus

        # we need to simulate an enclosing site manager:
        from zope.app.container.contained import Contained
        services = Contained()
        from zope.app.site.interfaces import ISiteManager
        zope.interface.directlyProvides(services, ISiteManager)
        reg.__parent__ = services

        # we need an event. Initially, we create an event simulating delete
        # of the services.  In this case, nothing should change:
        from zope.app.container.contained import ObjectRemovedEvent
        event = ObjectRemovedEvent(services)
        SimpleRegistrationRemoveSubscriber(reg, event)
        self.assertEquals(reg.status, ActiveStatus)

        # Now we'll "remove" the registration:
        event = ObjectRemovedEvent(reg)

        # test that removal fails with Active status
        self.assertRaises(DependencyError,
                          SimpleRegistrationRemoveSubscriber, reg, event)

        # test that removal succeeds with Registered status
        reg.status = RegisteredStatus
        SimpleRegistrationRemoveSubscriber(reg, event)

        self.assertEquals(reg.status, UnregisteredStatus)
        
class TestSimpleRegistration(TestCase):

    def setUp(self):
        # XXX: May need more setup related to Adapter service?
        # We can't use the status property on a SimpleRegistration instance.
        # we disable it for these tests
        self.__oldprop = SimpleRegistration.status
        del SimpleRegistration.status

    def tearDown(self):
        # Restore the status prop
        SimpleRegistration.status = self.__oldprop

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

class TestComponentRegistrationEvents:
    def test_addNotify(self):
        """
        First we create a dummy registration
        
          >>> reg = DummyRegistration()

        Now call notification

          >>> ComponentRegistrationAddSubscriber(reg, None)

        Check to make sure the adapter added the path

          >>> reg.dependents()
          ('dummy!',)
        """
        
    def test_removeNotify_dependents(self):
        """
        First we create a dummy registration
        
          >>> reg = DummyRegistration()

        Now call notification

          >>> ComponentRegistrationAddSubscriber(reg, None)

        Check to make sure the adapter added the path

          >>> reg.dependents()
          ('dummy!',)

        Now remove notify:

          >>> ComponentRegistrationRemoveSubscriber(reg, None)

        Check to make sure the adapter removed the dependencie(s).

          >>> reg.dependents()
          ()
        
        """

def test_suite():
    import sys
    return TestSuite((
        makeSuite(TestSimpleRegistration),
        makeSuite(TestComponentRegistration),
        makeSuite(TestSimpleRegistrationEvents),
        DocTestSuite(),
        DocTestSuite('zope.app.registration.registration'),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
