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

$Id: test_view.py,v 1.2 2002/12/25 14:13:20 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.iconfigurable import TestingIConfigurable
from zope.app.services.view import ViewService
from zope.interface import Interface
from zope.proxy.context import ContextWrapper
from zope.component.exceptions import ComponentLookupError
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.service import ServiceManager
from zope.app.services.view import ViewConfiguration
from zope.app.content.folder import RootFolder
from zope.component import getServiceManager
from zope.app.traversing import traverse
from zope.component.interfaces import IServiceService
from zope.component.view import provideView
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.interfaces.services.interfaces import IZPTTemplate
from zope.app.services.view import PageConfiguration, BoundTemplate
from zope.interface.verify import verifyObject
from zope.component.interfaces import IViewService

class I1(Interface):
    pass

class I1E(I1):
    pass

I2 = IBrowserPresentation

class I3(Interface):
    pass

class I4(Interface):
    pass


class Configuration:
    forInterface = I1
    presentationType = I2
    viewName = 'test'
    layer = 'default'

    def getView(self, object, request):
        return self.factory(object, request)

    def activated(self): pass
    def deactivated(self): pass

class C: pass

class A:
    def __init__(self, object, request):
        self.context = object
        self.request = request


class TestViewService(PlacefulSetup, TestingIConfigurable, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
        self._service = ContextWrapper(ViewService(), self.rootFolder)

    def test_implements_IViewService(self):
        from zope.component.interfaces import IViewService
        from zope.interface.verify import verifyObject

        verifyObject(IViewService, self._service)


    def createTestingConfigurable(self):
        return ContextWrapper(ViewService(), C())

    def createTestingConfiguration(self):
        return Configuration()

    def test_implements_IViewService(self):
        verifyObject(IViewService, ViewService())

    def test_queryView_no_view(self):
        service = self._service
        class O:
            __implements__ = I1

        o = O()
        request = TestRequest()
        self.assertEqual(service.queryView(o, 'test', request), None)
        self.assertEqual(service.queryView(o, 'test', request, 42), 42)

    def test_getView_no_view(self):
        service = self._service
        class O:
            __implements__ = I1

        o = O()
        request = TestRequest()
        self.assertRaises(ComponentLookupError,
                          service.getView, O(), 'test', request)

    def test_queryView_and_getView(self):
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
        request = TestRequest()

        for m in 'queryView', 'getView':
            for r in I1, I1E:
                o = O()
                o.__implements__ = r

                view = getattr(service, m)(o, 'test', request)
                self.assertEqual(view.__class__, A)
                self.assertEqual(view.context, o)
                self.assertEqual(view.request, request)

    def test_queryView_delegation(self):
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
        registry = self._service.queryConfigurationsFor(Configuration())

        for args in ((), (I1E, ), (None, I2), (I1E, I2), ):
            r = self._service.getRegisteredMatching(*args)
            self.assertEqual(list(r), [(I1, I2, registry, 'default', 'test')])

class PhonyServiceManager(ServiceManager):

    __implements__ = IServiceService

    def resolve(self, name):
        if name == 'Foo.Bar.A':
            return A

class TestViewConfiguration(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        rootFolder = RootFolder()
        rootFolder.setServiceManager(PhonyServiceManager())
        self.configuration = ContextWrapper(
            ViewConfiguration(I1, 'test', IBrowserPresentation, "Foo.Bar.A"),
            rootFolder,
            )

    def test_getView(self):
        c = C()
        request = TestRequest()
        view = self.configuration.getView(c, request)
        self.assertEqual(view.__class__, A)
        self.assertEqual(view.context, c)
        self.assertEqual(view.request, request)
        self.assertEqual(self.configuration.forInterface, I1)
        self.assertEqual(self.configuration.presentationType, I2)

class PhonyTemplate:

    __implements__ = IZPTTemplate

class TestPageConfiguration(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        rootFolder = RootFolder()
        rootFolder.setServiceManager(PhonyServiceManager())
        default = traverse(rootFolder, '++etc++Services/Packages/default')
        self.__template = PhonyTemplate()
        default.setObject('t', self.__template)
        self.__configuration = ContextWrapper(
            PageConfiguration(I1, 'test', IBrowserPresentation,
                              "Foo.Bar.A",
                              '/++etc++Services/Packages/default/t',
                              ),
            rootFolder,
            )

    def test_getView(self):
        c = C()
        request = TestRequest()
        view = self.__configuration.getView(c, request)
        self.assertEqual(view.__class__, BoundTemplate)
        self.assertEqual(view.template, self.__template)

        view = view.view
        self.assertEqual(view.__class__, A)
        self.assertEqual(view.context, c)
        self.assertEqual(view.request, request)
        self.assertEqual(self.__configuration.forInterface, I1)
        self.assertEqual(self.__configuration.presentationType, I2)

def test_suite():
    return TestSuite((
        makeSuite(TestViewService),
        makeSuite(TestViewConfiguration),
        makeSuite(TestPageConfiguration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
