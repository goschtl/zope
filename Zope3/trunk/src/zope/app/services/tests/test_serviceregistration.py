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

$Id: test_serviceregistration.py,v 1.3 2003/12/18 09:57:15 pnaveen Exp $
"""

from unittest import TestCase, main, makeSuite

from zope.interface import Interface, implements

from zope.component import getServiceManager, getAdapter
from zope.app.traversing import traverse, getPath
from zope.app.services.service import ServiceRegistration
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.component.service import defineService
from zope.app.interfaces.services.service import IBindingAware
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.services.service import ISimpleService

from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.dependable import DependencyError

class ITestService(Interface):
    pass

class TestServiceBase:
    __name__ = __parent__ = None
    implements(ITestService, IBindingAware, IDependable)
    
    _bound = _unbound = ()

    def bound(self, name):
        self._bound += (name, )

    def unbound(self, name):
        self._unbound += (name, )

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

class TestService(TestServiceBase):
    implements(ISimpleService)

class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)

        defineService('test_service', ITestService)

        default = traverse(self.rootFolder,
                           '++etc++site/default')
        self.__default = default

        default['c'] = TestService()

        registration = ServiceRegistration(
            'test_service', '/++etc++site/default/c')

        self.__c = traverse(default, 'c')
        self.__cm = default.getRegistrationManager()

        self.__registration_name = self.__cm.addRegistration(registration)

        self.__config = traverse(self.__cm, self.__registration_name)
        self.__configpath = getPath(self.__config)

    def test_activated(self):
        old = self.__c._bound
        self.__config.activated()
        self.assertEqual(self.__c._bound, old+('test_service',))

    def test_deactivated(self):
        old = self.__c._unbound
        self.__config.deactivated()
        self.assertEqual(self.__c._unbound, old+('test_service',))

    def test_getInterface(self):
        self.assertEquals(self.__config.getInterface(), ITestService)

    # XXX the following tests check the same things as
    # zope.app.services.tests.testregistrations, but in a different way

    def test_getComponent(self):
        self.assertEqual(self.__config.getComponent(), self.__c)

    def test_addNotify(self):
        self.assertEqual(self.__c._dependents,
                         (self.__configpath, ))
        u = getAdapter(self.__c, IRegistered)
        self.assertEqual(list(u.usages()),
                         [self.__configpath])

    def test_removeNotify_and_unregistered(self):
        self.__config.status = RegisteredStatus

        sm = getServiceManager(self.__default)
        registry = sm.queryRegistrationsFor(self.__config)
        self.failUnless(registry, "The components should be registered")

        del self.__cm[self.__registration_name]
        self.assertEqual(self.__c._dependents, ())
        u = getAdapter(self.__c, IRegistered)
        self.assertEqual(len(u.usages()), 0)

        self.failIf(registry, "The components should not be registered")

    def test_disallow_delete_when_active(self):
        self.__config.status = ActiveStatus
        try:
            del self.__cm[self.__registration_name]
        except DependencyError:
            pass # OK
        else:
            self.fail("Should have gotten a dependency error")

    def test_not_a_local_service(self):
        defineService('test_service_2', ITestService)
        self.__default['c2'] = TestServiceBase()

        self.assertRaises(
            TypeError,
            ServiceRegistration,
            'test_service',
            '/++etc++site/default/c2',
            self.__default
            )


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
