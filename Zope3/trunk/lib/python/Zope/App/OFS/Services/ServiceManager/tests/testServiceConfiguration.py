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

$Id: testServiceConfiguration.py,v 1.2 2002/11/30 18:39:18 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Interface import Interface

from Zope.ComponentArchitecture import getServiceManager
from Zope.App.Traversing import traverse
from Zope.App.OFS.Services.ServiceManager.ServiceConfiguration \
     import ServiceConfiguration
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.OFS.Services.ServiceManager.ServiceManager \
     import ServiceManager
from Zope.ComponentArchitecture.GlobalServiceManager \
     import serviceManager
from Zope.App.OFS.Services.ServiceManager.IBindingAware \
     import IBindingAware
from Zope.App.OFS.Services.ConfigurationInterfaces \
     import Active, Unregistered, Registered

from Zope.App.DependencyFramework.IDependable import IDependable
from Zope.App.DependencyFramework.Exceptions import DependencyError

from Zope.App.OFS.Container.ZopeContainerAdapter import ZopeContainerAdapter


class ITestService(Interface):
    pass

class TestService:
    __implements__ = ITestService, IBindingAware, IDependable

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

class Test(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        serviceManager.defineService('test_service', ITestService)
        default = traverse(self.rootFolder,
                           '++etc++Services/Packages/default')
        self.__default = default

        default.setObject('c', TestService())


        configuration = ServiceConfiguration(
            'test_service', '/++etc++Services/Packages/default/c')

        self.__c = traverse(default, 'c')
        self.__cm = ZopeContainerAdapter(traverse(default, "configure"))
        
        self.__cm.setObject('', configuration)

        self.__config = traverse(default, 'configure/1')

    def test_getService(self):
        self.assertEqual(self.__config.getService(), self.__c)

    def test_activated(self):
        old = self.__c._bound
        self.__config.activated()
        self.assertEqual(self.__c._bound, old+('test_service',))

    def test_deactivated(self):
        old = self.__c._unbound
        self.__config.deactivated()
        self.assertEqual(self.__c._unbound, old+('test_service',))

    def test_manage_afterAdd(self):
        self.assertEqual(self.__c._dependents,
                         ('/++etc++Services/Packages/default/configure/1', ))

    def test_manage_beforeDelete_and_unregistered(self):
        self.__config.status = Registered

        sm = getServiceManager(self.__default)
        registry = sm.queryConfigurationsFor(self.__config)
        self.failUnless(registry, "The components should be registered")

        del self.__cm['1']
        self.assertEqual(self.__c._dependents, ())

        self.failIf(registry, "The components should not be registered")

    def test_disallow_delete_when_active(self):
        self.__config.status = Active
        try:
            del self.__cm['1']
        except DependencyError:
            pass # OK
        else:
            self.failUnless(0, "Should have gotten a depency error")
            

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
