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

$Id: test_serviceconfiguration.py,v 1.7 2003/03/23 22:03:28 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface import Interface

from zope.component import getServiceManager, getAdapter
from zope.app.traversing import traverse, getPath
from zope.app.services.service import ServiceConfiguration
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.service import ServiceManager
from zope.component.service import defineService
from zope.app.interfaces.services.service import IBindingAware
from zope.app.interfaces.services.configuration import Active, Unregistered
from zope.app.interfaces.services.configuration import Registered
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.interfaces.services.service import ISimpleService

from zope.app.interfaces.dependable import IDependable
from zope.app.interfaces.dependable import DependencyError

from zope.app.container.zopecontainer import ZopeContainerAdapter


class ITestService(Interface):
    pass

class TestServiceBase:
    __implements__ = (ITestService, IBindingAware, IDependable)

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
    __implements__ = TestServiceBase.__implements__, ISimpleService

class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        defineService('test_service', ITestService)
        default = traverse(self.rootFolder,
                           '++etc++Services/default')
        self.__default = default

        default.setObject('c', TestService())


        configuration = ServiceConfiguration(
            'test_service', '/++etc++Services/default/c')

        self.__c = traverse(default, 'c')
        self.__cm = ZopeContainerAdapter(default.getConfigurationManager())

        self.__cm.setObject('', configuration)

        self.__config = traverse(default.getConfigurationManager(), '1')
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
    # zope.app.services.tests.testconfigurations, but in a different way

    def test_getComponent(self):
        self.assertEqual(self.__config.getComponent(), self.__c)

    def test_afterAddHook(self):
        self.assertEqual(self.__c._dependents,
                         (self.__configpath, ))
        u = getAdapter(self.__c, IUseConfiguration)
        self.assertEqual(list(u.usages()),
                         [self.__configpath])

    def test_beforeDeleteHook_and_unregistered(self):
        self.__config.status = Registered

        sm = getServiceManager(self.__default)
        registry = sm.queryConfigurationsFor(self.__config)
        self.failUnless(registry, "The components should be registered")

        del self.__cm['1']
        self.assertEqual(self.__c._dependents, ())
        u = getAdapter(self.__c, IUseConfiguration)
        self.assertEqual(len(u.usages()), 0)

        self.failIf(registry, "The components should not be registered")

    def test_disallow_delete_when_active(self):
        self.__config.status = Active
        try:
            del self.__cm['1']
        except DependencyError:
            pass # OK
        else:
            self.failUnless(0, "Should have gotten a depency error")

    def test_not_a_local_service(self):
        defineService('test_service_2', ITestService)
        self.__default.setObject('c2', TestServiceBase())

        self.assertRaises(
            TypeError,
            ServiceConfiguration,
            'test_service',
            '/++etc++Services/default/c2',
            self.__default
            )


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
