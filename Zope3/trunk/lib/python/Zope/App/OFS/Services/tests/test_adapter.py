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
"""Test the adapter module

$Id: test_adapter.py,v 1.2 2002/12/19 20:38:26 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from TestingIConfigurable import TestingIConfigurable
from Zope.App.OFS.Services.adapter import AdapterService
from Interface import Interface
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
     import PlacefulSetup
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager
from Zope.App.OFS.Services.adapter import AdapterConfiguration
from Zope.App.OFS.Content.Folder.RootFolder import RootFolder
from Zope.ComponentArchitecture import getServiceManager
from Zope.App.Traversing import traverse
from Zope.ComponentArchitecture.IServiceService import IServiceService
from Zope.ComponentArchitecture.GlobalAdapterService import provideAdapter

class I1(Interface):
    pass

class I1E(I1):
    pass

class I2B(Interface):
    pass

class I2(I2B):
    pass

class I3(Interface):
    pass

class I4(Interface):
    pass


class Configuration:
    forInterface = I1
    providedInterface = I2

    def getAdapter(self, object):
        return self.factory(object)

    def activated(self): pass
    def deactivated(self): pass

class C: pass

class A:
    def __init__(self, object):
        self.context = object


class TestAdapterService(PlacefulSetup, TestingIConfigurable, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        self._service = ContextWrapper(AdapterService(), self.rootFolder)


    def test_implements_IAdapterService(self):
        from Zope.ComponentArchitecture.IAdapterService import IAdapterService
        from Interface.Verify import verifyObject

        verifyObject(IAdapterService, self._service)

    def createTestingConfigurable(self):
        return ContextWrapper(AdapterService(), C())

    def createTestingConfiguration(self):
        return Configuration()

    def test_queryAdapter_no_adapter(self):
        service = self._service
        class O:
            __implements__ = I1

        o = O()
        self.assertEqual(service.queryAdapter(o, I2), None)
        self.assertEqual(service.queryAdapter(o, I2, 42), 42)

        self.assertEqual(service.queryAdapter(o, I1), o)
        self.assertEqual(service.queryAdapter(o, I1, 42), o)

    def test_getAdapter_no_adapter(self):
        service = self._service
        class O:
            __implements__ = I1

        o = O()
        self.assertRaises(ComponentLookupError, service.getAdapter, O(), I2)
        self.assertEqual(service.getAdapter(o, I1), o)

    def test_queryAdapter_and_getAdapter(self):
        service = self._service

        sm = traverse(self.rootFolder, '++etc++Services')

        configure = traverse(sm, 'Packages/default/configure')
        configuration = Configuration()
        configure.setObject('', configuration)
        configuration = traverse(configure, '1')

        class O:
            __implements__ = I1

        configuration.factory = A
        
        registry = service.createConfigurationsFor(configuration)
        registry.register(configuration)
        registry.activate(configuration)

        o = O()

        for m in 'queryAdapter', 'getAdapter':
            for r in I1, I1E:
                for p in I2B, I2:
                    o = O()
                    o.__implements__ = r

                    adapter = getattr(service, m)(o, p)
                    self.assertEqual(adapter.__class__, A)
                    self.assertEqual(adapter.context, o)

            self.assertEqual(getattr(service, m)(o, I1), o)

        self.assertEqual(service.queryAdapter(o, I3), None)
        self.assertEqual(service.queryAdapter(o, I3, 42), 42)
        self.assertRaises(ComponentLookupError, service.getAdapter, O(), I3)

    def test_queryAdapter_delegation(self):
        service = self._service
        
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())

        sm = traverse(self.rootFolder, '++etc++Services')

        configure = traverse(sm, 'Packages/default/configure')
        configuration = Configuration()
        configure.setObject('', configuration)
        configuration = traverse(configure, '1')

        class O:
            __implements__ = I1

        configuration.factory = A

        registry = service.createConfigurationsFor(configuration)
        registry.register(configuration)
        registry.activate(configuration)

        o = O()

        class A2(A): pass

        provideAdapter(I1, I4, A2)
    
        adapter = service.queryAdapter(o, I4)
        self.assertEqual(adapter.__class__, A2)
        self.assertEqual(adapter.context, o)

    def test_queryAdapter_delegation_w_no_adapters_locally(self):
        service = self._service

        class O:
            __implements__ = I1

        o = O()

        class A2(A): pass

        provideAdapter(I1, I4, A2)
    
        adapter = service.queryAdapter(o, I4)
        self.assertEqual(adapter.__class__, A2)
        self.assertEqual(adapter.context, o)

    def test_getRegisteredMatching(self):
        self.test_queryAdapter_and_getAdapter()
        registry = self._service.queryConfigurations(I1, I2, '')

        for args in ((), (I1E, ), (None, I2), (I1E, I2), ):
            r = self._service.getRegisteredMatching(*args)
            self.assertEqual(list(r), [(I1, I2, registry)])

class PhonyServiceManager:

    __implements__ = IServiceService

    def resolve(self, name):
        if name == 'Foo.Bar.A':
            return A
        
class TestAdapterConfiguration(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        rootFolder = RootFolder()
        rootFolder.setServiceManager(PhonyServiceManager())
        self.configuration = ContextWrapper(
            AdapterConfiguration(I1, I2, "Foo.Bar.A"),
            rootFolder,
            )
    
    def test_getAdapter(self):
        c = C()
        adapter = self.configuration.getAdapter(c)
        self.assertEqual(adapter.__class__, A)
        self.assertEqual(adapter.context, c)
        self.assertEqual(self.configuration.forInterface, I1)
        self.assertEqual(self.configuration.providedInterface, I2)

def test_suite():
    return TestSuite((
        makeSuite(TestAdapterService),
        makeSuite(TestAdapterConfiguration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
