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
"""Test the presentation module

$Id: test_presentation.py,v 1.2 2003/11/21 17:09:59 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.app import zapi
from zope.interface import Interface, directlyProvides, implements
from zope.interface.verify import verifyObject

from zope.app.content.folder import rootFolder
from zope.app.services.zpt import IZPTTemplate
from zope.app.services.service import ServiceManager
from zope.app.services.servicenames import Presentation
from zope.app.services.tests.iregistry import TestingIRegistry
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.presentation import ViewRegistration
from zope.app.services.presentation import PageRegistration
from zope.app.services.presentation import BoundTemplate
from zope.app.services.presentation import LocalPresentationService
from zope.app.tests import setup
from zope.app.traversing import traverse

from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.component.interfaces import IPresentationService
from zope.app.tests import ztapi
from zope.configuration.exceptions import ConfigurationError

from zope.proxy import removeAllProxies

from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.container.contained import contained

class I1(Interface):
    pass

class I1E(I1):
    pass

I2 = IBrowserRequest

class I3(Interface):
    pass

class I4(Interface):
    pass


class Registration:
    required = I1
    requestType = I2
    name = 'test'
    layer = 'default'
    serviceType = Presentation
    provided = Interface

    with = property(lambda self: (self.requestType, ))
    factories = property(lambda self: (self.factory, ))

    def activated(self): pass
    def deactivated(self): pass

class C: pass

class PhonyTemplate:

    implements(IZPTTemplate)

class A:
    def __init__(self, object, request):
        self.context = object
        self.request = request

    run = PhonyTemplate()

class TestLocalPresentationService(PlacefulSetup, TestingIRegistry, TestCase):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)
        self._service = setup.addService(sm, Presentation,
                                         LocalPresentationService())

    def test_defaultSkin(self):
        # XXX we don't let people set the default skin locally yet.
        # So just test that we can get the default from the global service
        zapi.getService(None, Presentation).defineSkin('bob', ['default'])
        zapi.getService(None, Presentation).setDefaultSkin('bob')
        self.assertEqual(self._service.defaultSkin, 'bob')

    def test_querySkin(self):
        # XXX we don't let people define skins locally yet.
        # So just test that we can get the defs from the global service
        globalService = zapi.getService(None, Presentation)
        globalService.defineLayer('bob')
        globalService.defineSkin('bob', ['bob', 'default'])
        self.assertEqual(self._service.querySkin('bob'), ('bob', 'default'))
        
    def test_queryLayer(self):
        # XXX we don't let people define layers locally yet.
        # So just test that we can get the them from the global service
        globalService = zapi.getService(None, Presentation)
        layer = self._service.queryLayer('default')
        self.assertEqual(layer.__parent__, globalService)
        self.test_queryView()
        layer = self._service.queryLayer('default')
        self.assertEqual(layer.__parent__, self._service)

    def test_queryDefaultViewName(self):
        # XXX we don't let people define the default view name locally
        # yet.  So just test that we can get it from the global
        # service
        class O:
            implements(I1)
        o = O()
        r = TestRequest()
        self.assertEqual(self._service.queryDefaultViewName(o, r),
                         None)
        globalService = zapi.getService(None, Presentation)
        globalService.setDefaultViewName(I1, IBrowserRequest, 'foo.html')
        self.assertEqual(self._service.queryDefaultViewName(o, r),
                         'foo.html')

    def test_queryMultiView(self):
        # XXX that we don't let people define multiviews locally yet.
        # So just test that we can get them from the global service
        class X:
            implements(I1)
        class Y:
            implements(I3)
        x = X()
        y = Y()
        r = TestRequest()
        self.assertEqual(self._service.queryMultiView((x, y), 'foo.html', r),
                         None)
        globalService = zapi.getService(None, Presentation)

        class MV:
            def __init__(self, x, y, request):
                self.x, self.y, self.request = x, y, request
                
        globalService.provideAdapter(IBrowserRequest, [MV], 'foo.html',
                                     contexts=(I1, I3))
        v = self._service.queryMultiView((x, y), 'foo.html', r)
        self.assertEqual(v.__class__, MV)
        self.assertEqual(v.request, r)
        self.assertEqual(v.x, x)
        self.assertEqual(v.y, y)
        

    def test_queryResource(self):
        # XXX that we don't let people define resources locally yet.
        # So just test that we can get them from the global service

        r = TestRequest()
        self.assertEqual(self._service.queryResource('logo.gif', r),
                         None)

        class Resource:
            def __init__(self, request):
                self.request = request

        globalService = zapi.getService(None, Presentation)
        globalService.provideResource('logo.gif', IBrowserRequest, Resource)
        
        resource = self._service.queryResource('logo.gif', r)
        self.assertEqual(resource.__class__, Resource)
        self.assertEqual(resource.request, r)

    def test_implements_IPresentationService(self):
        from zope.component.interfaces import IPresentationService

        verifyObject(IPresentationService, self._service)

    def createTestingRegistry(self):
        return contained(LocalPresentationService(), C())

    def createTestingRegistration(self):
        return Registration()

    def test_implements_IPresentationService(self):
        verifyObject(IPresentationService, LocalPresentationService())

    def test_queryView_no_view(self):
        service = self._service
        class O:
            implements(I1)

        o = O()
        request = TestRequest()
        self.assertEqual(service.queryView(o, 'test', request), None)
        self.assertEqual(service.queryView(o, 'test', request, default=42), 42)

    def test_queryView(self):
        sm = traverse(self.rootFolder, '++etc++site')

        registration_manager = traverse(sm, 'default').getRegistrationManager()
        key = registration_manager.addRegistration(Registration())
        registration = traverse(registration_manager, key)

        class O:
            implements(I1)

        registration.factory = A

        registry = self._service.createRegistrationsFor(registration)
        registry.register(registration)
        registry.activate(registration)

        o = O()
        request = TestRequest()

        for r in I1, I1E:
            o = O()
            directlyProvides(o, r)

            view = self._service.queryView(o, 'test', request)
            self.assertEqual(view.__class__, A)
            self.assertEqual(view.context, o)
            self.assertEqual(view.request, request)

    def test_queryView_delegation(self):
        service = self._service

        sm = self.buildFolders(site=True)
        registration_manager = traverse(sm, 'default').getRegistrationManager()
        registration = Registration()
        name = registration_manager.addRegistration(registration)
        registration = traverse(registration_manager, name)

        class O:
            implements(I1)

        o = O()
        request = TestRequest()

        class A2(A): pass

        ztapi.browserView(I1, 'test', A2)

        view = service.queryView(o, 'test', request)
        self.assertEqual(view.__class__, A2)
        self.assertEqual(view.context, o)
        self.assertEqual(view.request, request)

    def test_getRegistrationsForInterface(self):
        self.test_queryView()
        for reg in self._service.getRegistrationsForInterface(I1):
            if reg.required is None:
                continue
            self.assertEqual(reg.required, I1)

        for reg in self._service.getRegistrationsForInterface(I1E):
            if reg.required is None:
                continue
            self.assertEqual(reg.required, I1)


class PhonyServiceManager(ServiceManager):

    implements(IServiceService)

class ModuleFinder:

    def resolve(self, name):
        if name == "Foo.Bar.A":
            return A
        raise ImportError(name)


class TestViewRegistration(PlacefulSetup, TestCase):

    def test_factories(self):
        folder = ModuleFinder()
        folder = contained(folder, folder)
        registration = contained(
            ViewRegistration(I1, 'test', I2, "Foo.Bar.A", 'zope.View'),
            folder,
            )

        self.assertEqual(registration.required, I1)
        self.assertEqual(registration.requestType, I2)

        factory, = registration.factories
        self.assertEqual(factory, A)


class TestPageRegistration(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.rootFolder = rootFolder()
        self.rootFolder.setSiteManager(PhonyServiceManager(self.rootFolder))
        default = traverse(self.rootFolder, '++etc++site/default')
        self.__template = PhonyTemplate()
        default['t'] = self.__template
        self.folder = contained(ModuleFinder(), self.rootFolder)
        self.folder = contained(ModuleFinder(), self.folder)

    def test_factories_template(self):
        registration = contained(
            PageRegistration(I1, 'test', 'zope.View',
                              "Foo.Bar.A",
                              template='/++etc++site/default/t',
                              ),
            self.folder,
            )

        c = C()
        request = TestRequest()
        factory, = registration.factories
        view = factory(c, request)
        self.assertEqual(view.__class__, BoundTemplate)
        self.assertEqual(removeAllProxies(view).template, self.__template)

        view = removeAllProxies(view).view
        self.assert_(issubclass(view.__class__, A))
        self.assertEqual(view.context, c)
        self.assertEqual(view.request, request)
        self.assertEqual(registration.required, I1)
        self.assertEqual(registration.requestType, I2)

    def test_factories_attribute(self):
        registration = contained(
            PageRegistration(
                I1, 'test', 'zope.View', "Foo.Bar.A", attribute='run'),
            self.folder,
            )
        c = C()
        request = TestRequest()
        factory, = registration.factories
        view = factory(c, request)
        self.assertEquals(view, A.run)

    def test_factories_errors(self):
        registration = contained(
            PageRegistration(I1, 'test', 'zope.View', "Foo.Bar.A"),
            self.folder,
            )
        c = C()
        request = TestRequest()
        self.assertRaises(ConfigurationError, lambda: registration.factories)
        registration.template = '/++etc++site/default/t'
        registration.attribute = 'run'
        self.assertRaises(ConfigurationError, lambda: registration.factories)


def test_suite():
    return TestSuite([
        makeSuite(TestLocalPresentationService),
        makeSuite(TestViewRegistration),
        makeSuite(TestPageRegistration),
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
