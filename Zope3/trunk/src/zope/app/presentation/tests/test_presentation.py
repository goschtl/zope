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

$Id$
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.doctestunit import DocTestSuite
from zope.app.tests.placelesssetup import setUp, tearDown

from zope.app import zapi
from zope.interface import Interface, directlyProvides, implements
from zope.interface.verify import verifyObject

from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from zope.app.folder import rootFolder
from zope.app.presentation.zpt import IZPTTemplate
from zope.app.site.service import ServiceManager
from zope.app.servicenames import Presentation
from zope.app.registration.tests.iregistry import TestingIRegistry
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.presentation.presentation import ViewRegistration
from zope.app.presentation.presentation import PageRegistration
from zope.app.presentation.presentation import BoundTemplate
from zope.app.presentation.presentation import LocalPresentationService
from zope.app.presentation.presentation import IPageRegistration
from zope.app.presentation.presentation import PageRegistrationAddSubscriber
from zope.app.presentation.presentation import PageRegistrationRemoveSubscriber
from zope.app.tests import setup
from zope.app.traversing.api import traverse

from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.component.interfaces import IPresentationService
from zope.app.tests import ztapi
from zope.configuration.exceptions import ConfigurationError

from zope.proxy import removeAllProxies

from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.app.container.contained import contained, uncontained, setitem
from zope.app.container.interfaces import IContained, ILocation

from zope.app.dependable.interfaces import IDependable
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.registration.interfaces import IRegistered
from zope.app.traversing.interfaces import IPhysicallyLocatable
from zope.app.dependable import Dependable

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

    def __repr__(self):
        return 'Registration(%s)' % self.factory.__name__

class C: pass

class PhonyTemplate:
    __name__ = __parent__ = None
    implements(IZPTTemplate, IDependable, IRegistered)

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
        zapi.getGlobalService(Presentation).defineSkin('bob', ['default'])
        zapi.getGlobalService(Presentation).setDefaultSkin('bob')
        self.assertEqual(self._service.defaultSkin, 'bob')

    def test_querySkin(self):
        # XXX we don't let people define skins locally yet.
        # So just test that we can get the defs from the global service
        globalService = zapi.getGlobalService(Presentation)
        globalService.defineLayer('bob')
        globalService.defineSkin('bob', ['bob', 'default'])
        self.assertEqual(self._service.querySkin('bob'), ('bob', 'default'))
        
    def test_queryLayer(self):
        # XXX we don't let people define layers locally yet.
        # So just test that we can get the them from the global service
        globalService = zapi.getGlobalService(Presentation)
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
        globalService = zapi.getGlobalService(Presentation)
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
        self.assertEqual(self._service.queryMultiView((x, y), r,
                                                      name='foo.html'),
                         None)
        globalService = zapi.getGlobalService(Presentation)

        class MV:
            def __init__(self, x, y, request):
                self.x, self.y, self.request = x, y, request
                
        globalService.provideAdapter(IBrowserRequest, MV, 'foo.html',
                                     contexts=(I1, I3))
        v = self._service.queryMultiView((x, y), r, name='foo.html')
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

        globalService = zapi.getGlobalService(Presentation)
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

    def test_registrations(self):
        self.test_queryView()
        registrations = map(str, self._service.registrations())
        registrations.sort()
        self.assertEqual(
            registrations,

            ['Registration(A)',

             # These were set up by PlacefulSetup:
             "zope.component.presentation.PresentationRegistration("
               "default, ('IContainmentRoot', 'IBrowserRequest'), "
               "'Interface', 'absolute_url', 'SiteAbsoluteURL', '')",
             "zope.component.presentation.PresentationRegistration("
               "default, (None, 'IBrowserRequest'), 'IAbsoluteURL', "
               "'', 'AbsoluteURL', '')",
             "zope.component.presentation.PresentationRegistration("
               "default, (None, 'IBrowserRequest'), 'Interface', "
               "'absolute_url', 'AbsoluteURL', '')",
             "zope.component.presentation.PresentationRegistration("
               "default, (None, None), "
               "'ITraversable', 'etc', 'etc', '')",
             ]
            )

    def test_localOnly_registrations(self):
        self.test_queryView()
        registrations = map(str, self._service.registrations(localOnly=True))
        registrations.sort()
        self.assertEqual(registrations, ['Registration(A)'])

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

    implements(IContained)

    __parent__ = __name__ = None

    def __init__(self):
        self._dict = {}

    def resolve(self, name):
        if name == "Foo.Bar.A":
            return A
        raise ImportError(name)

    def __setitem__(self, key, ob):
        setitem(self, self.__setitem, key, ob)
    
    def __setitem(self, key, ob):
        self._dict[key] = ob

    def get(self, key, default=None):
        return self._dict.get(key, default)


class PhonyPathAdapter:
    implements(IPhysicallyLocatable)

    def __init__(self, context):
        self.context = context

    def getPath(self):
        return self.context.__name__

    def getRoot(self):
        root = self.context
        while root.__parent__ is not None:
            root = root.__parent__
        return root


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

        factory = registration.factory
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
        factory = registration.factory
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
            self.folder,6
            )
        c = C()
        request = TestRequest()
        factory = registration.factory
        view = factory(c, request)
        self.assertEquals(view, A.run)

    def test_factories_errors(self):
        registration = contained(
            PageRegistration(I1, 'test', 'zope.View', "Foo.Bar.A"),
            self.folder,
            )
        c = C()
        request = TestRequest()
        self.assertRaises(ConfigurationError, lambda: registration.factory)
        registration.template = '/++etc++site/default/t'
        registration.attribute = 'run'
        self.assertRaises(ConfigurationError, lambda: registration.factory)

    def test_registerAddSubscriber_template(self):
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             PhonyPathAdapter)
        ztapi.handle((IPageRegistration, IObjectAddedEvent),
                     PageRegistrationAddSubscriber)
        registration = PageRegistration(I1, 'test', 'zope.View', "Foo.Bar.A",
                                        template='/++etc++site/default/t')
        
        # Test add event
        self.folder['test'] = registration
        dependents = zapi.getAdapter(self.__template, IDependable)
        self.assert_('test' in dependents.dependents())

    def test_registerRemoveSubscriber_template(self):
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             PhonyPathAdapter)
        ztapi.handle((IPageRegistration, IObjectRemovedEvent),
                     PageRegistrationRemoveSubscriber)
        registration = PageRegistration(I1, 'test', 'zope.View', "Foo.Bar.A",
                                        template='/++etc++site/default/t')

        # Test remove event
        self.folder['test'] = registration
        uncontained(registration, self.folder, 'test')
        dependents = zapi.getAdapter(self.__template, IDependable)
        self.assert_('test' not in dependents.dependents())
        
    def test_addremoveNotify_attribute(self):
        ztapi.provideAdapter(ILocation, IPhysicallyLocatable,
                             PhonyPathAdapter)
        registration = PageRegistration(I1, 'test', 'zope.View',
                                        "Foo.Bar.A", attribute='run')
        # Just add and remove registration to see that no errors occur
        self.folder['test'] = registration
        uncontained(registration, self.folder, 'test')


def test_suite():
    return TestSuite([
        makeSuite(TestLocalPresentationService),
        makeSuite(TestViewRegistration),
        makeSuite(TestPageRegistration),
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')


