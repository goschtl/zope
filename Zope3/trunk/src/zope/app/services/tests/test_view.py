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
"""Test the view module

$Id: test_view.py,v 1.19 2003/06/24 15:38:04 jeremy Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface import Interface, directlyProvides, implements
from zope.interface.verify import verifyObject

from zope.app.content.folder import RootFolder
from zope.app.context import ContextWrapper
from zope.app.interfaces.services.view import IZPTTemplate
from zope.app.services.service import ServiceManager
from zope.app.services.servicenames import Views
from zope.app.services.tests.iregistry import TestingIRegistry
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.view  \
     import ViewRegistration, PageRegistration, BoundTemplate, ViewService
from zope.app.tests import setup
from zope.app.traversing import traverse

from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService
from zope.component.view import provideView
from zope.component.interfaces import IViewService

from zope.configuration.exceptions import ConfigurationError

from zope.proxy import removeAllProxies

from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPresentation

class I1(Interface):
    pass

class I1E(I1):
    pass

I2 = IBrowserPresentation

class I3(Interface):
    pass

class I4(Interface):
    pass


class Registration:
    forInterface = I1
    presentationType = I2
    viewName = 'test'
    layer = 'default'
    serviceType = Views

    def getView(self, object, request):
        return self.factory(object, request)

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

class TestViewService(PlacefulSetup, TestingIRegistry, TestCase):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)
        self._service = setup.addService(sm, Views, ViewService())

    def test_implements_IViewService(self):
        from zope.component.interfaces import IViewService
        from zope.interface.verify import verifyObject

        verifyObject(IViewService, self._service)


    def createTestingRegistry(self):
        return ContextWrapper(ViewService(), C())

    def createTestingRegistration(self):
        return Registration()

    def test_implements_IViewService(self):
        verifyObject(IViewService, ViewService())

    def test_queryView_no_view(self):
        service = self._service
        class O:
            implements(I1)

        o = O()
        request = TestRequest()
        self.assertEqual(service.queryView(o, 'test', request), None)
        self.assertEqual(service.queryView(o, 'test', request, 42), 42)

    def test_getView_no_view(self):
        service = self._service
        class O:
            implements(I1)

        o = O()
        request = TestRequest()
        self.assertRaises(ComponentLookupError,
                          service.getView, O(), 'test', request)

    def test_queryView_and_getView(self):
        sm = traverse(self.rootFolder, '++etc++site')

        registration_manager = traverse(sm, 'default').getRegistrationManager()
        key = registration_manager.setObject('', Registration())
        registration = traverse(registration_manager, key)

        class O:
            implements(I1)

        registration.factory = A

        registry = self._service.createRegistrationsFor(registration)
        registry.register(registration)
        registry.activate(registration)

        o = O()
        request = TestRequest()

        for m in 'queryView', 'getView':
            for r in I1, I1E:
                o = O()
                directlyProvides(o, r)

                view = getattr(self._service, m)(o, 'test', request)
                self.assertEqual(view.__class__, A)
                self.assertEqual(view.context, o)
                self.assertEqual(view.request, request)

    def test_queryView_delegation(self):
        service = self._service

        sm = self.buildFolders(site=True)
        registration_manager = traverse(sm, 'default').getRegistrationManager()
        registration = Registration()
        registration_manager.setObject('', registration)
        registration = traverse(registration_manager, '1')

        class O:
            implements(I1)

        o = O()
        request = TestRequest()

        class A2(A): pass

        provideView(I1, 'test', IBrowserPresentation, A2)

        view = service.queryView(o, 'test', request)
        self.assertEqual(view.__class__, A2)
        self.assertEqual(view.context, o)
        self.assertEqual(view.request, request)

    def test_getRegisteredMatching(self):
        self.test_queryView_and_getView()
        registry = self._service.queryRegistrationsFor(Registration())

        for args in ((), (I1E, ), (None, I2), (I1E, I2), ):
            r = self._service.getRegisteredMatching(*args)
            self.assertEqual(list(r), [(I1, I2, registry, 'default', 'test')])

    def test_getRegistrationsForInterface(self):
        self.test_queryView_and_getView()
        for reg in self._service.getRegistrationsForInterface(I1):
            self.assertEqual(reg.forInterface, I1)

        for reg in self._service.getRegistrationsForInterface(I1E):
            self.assertEqual(reg.forInterface, I1)

class PhonyServiceManager(ServiceManager):

    implements(IServiceService)

    def resolve(self, name):
        if name == 'Foo.Bar.A':
            return A

class TestViewRegistration(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        rootFolder = RootFolder()
        rootFolder.setServiceManager(PhonyServiceManager())
        self.registration = ContextWrapper(
            ViewRegistration(I1, 'test', IBrowserPresentation, "Foo.Bar.A",
                              'zope.View'),
            rootFolder,
            )

    def test_getView(self):
        c = C()
        request = TestRequest()
        view = self.registration.getView(c, request)
        self.assertEqual(view.__class__, A)
        self.assertEqual(view.context, c)
        self.assertEqual(view.request, request)
        self.assertEqual(self.registration.forInterface, I1)
        self.assertEqual(self.registration.presentationType, I2)


class TestPageRegistration(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.rootFolder = RootFolder()
        self.rootFolder.setServiceManager(PhonyServiceManager())
        default = traverse(self.rootFolder, '++etc++site/default')
        self.__template = PhonyTemplate()
        default.setObject('t', self.__template)

    def test_getView_template(self):
        registration = ContextWrapper(
            PageRegistration(I1, 'test', 'zope.View',
                              "Foo.Bar.A",
                              template='/++etc++site/default/t',
                              ),
            self.rootFolder,
            )

        c = C()
        request = TestRequest()
        view = registration.getView(c, request)
        self.assertEqual(view.__class__, BoundTemplate)
        self.assertEqual(removeAllProxies(view).template, self.__template)

        view = removeAllProxies(view).view
        self.assert_(issubclass(view.__class__, A))
        self.assertEqual(view.context, c)
        self.assertEqual(view.request, request)
        self.assertEqual(registration.forInterface, I1)
        self.assertEqual(registration.presentationType, I2)

    def test_getView_attribute(self):
        registration = ContextWrapper(
            PageRegistration(I1, 'test', 'zope.View',
                              "Foo.Bar.A",
                              attribute='run',
                              ),
            self.rootFolder,
            )
        c = C()
        request = TestRequest()
        view = registration.getView(c, request)
        self.assertEquals(view, A.run)

    def test_getView_errors(self):
        registration = ContextWrapper(
            PageRegistration(I1, 'test', 'zope.View',
                              "Foo.Bar.A",
                              ),
            self.rootFolder,
            )
        c = C()
        request = TestRequest()
        self.assertRaises(ConfigurationError, registration.getView, c, request)
        registration.template = '/++etc++site/default/t'
        registration.attribute = 'run'
        self.assertRaises(ConfigurationError, registration.getView, c, request)


def test_suite():
    return TestSuite([
        makeSuite(TestViewService),
        makeSuite(TestViewRegistration),
        makeSuite(TestPageRegistration),
        ])

if __name__ == '__main__':
    main(defaultTest='test_suite')
