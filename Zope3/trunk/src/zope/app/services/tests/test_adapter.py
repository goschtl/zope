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

$Id: test_adapter.py,v 1.22 2003/09/21 17:33:11 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.iregistry import TestingIRegistry
from zope.app.services.adapter import AdapterService
from zope.interface import Interface, directlyProvides, implements
from zope.component.exceptions import ComponentLookupError
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.services.adapter import AdapterRegistration
from zope.app.traversing import traverse
from zope.component.adapter import provideAdapter

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


def contained(o1, o2):
    o1.__parent__ = o2
    return o1

class Registration:
    forInterface = I1
    providedInterface = I2
    adapterName = ''

    def getAdapter(self, object):
        return self.factory(object)

    def activated(self): pass
    def deactivated(self): pass

class C: pass

class A:
    def __init__(self, object):
        self.context = object


class TestAdapterService(PlacefulSetup, TestingIRegistry, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        self._service = AdapterService()
        self._service.__parent__ = self.rootFolder

    def test_implements_IAdapterService(self):
        from zope.component.interfaces import IAdapterService
        from zope.interface.verify import verifyObject

        verifyObject(IAdapterService, self._service)

    def createTestingRegistry(self):
        return contained(AdapterService(), C())

    def createTestingRegistration(self):
        return Registration()

    def test_conforms(self):
        service = self._service
        class Conforms:
            def __conform__(self, i):
                if i is I1:
                    return A(self)

        o = Conforms()
        self.assertEqual(service.queryAdapter(o, I2), None)
        self.assertRaises(ComponentLookupError, service.getAdapter, o, I2)
        self.assertEqual(service.queryAdapter(Conforms, I2), None)
        self.assertEqual(service.queryAdapter(Conforms, I1), None)

        a = service.queryAdapter(o, I1)
        self.assertEqual(a.__class__, A)
        self.assertEqual(a.context, o)

        a = service.getAdapter(o, I1)
        self.assertEqual(a.__class__, A)
        self.assertEqual(a.context, o)

    def test_queryAdapter_no_adapter(self):
        service = self._service
        class O:
            implements(I1)

        o = O()
        self.assertEqual(service.queryAdapter(o, I2), None)
        self.assertEqual(service.queryAdapter(o, I2, 42), 42)

        self.assertEqual(service.queryAdapter(o, I1), o)
        self.assertEqual(service.queryAdapter(o, I1, 42), o)

    def test_getAdapter_no_adapter(self):
        service = self._service
        class O:
            implements(I1)

        o = O()
        self.assertRaises(ComponentLookupError, service.getAdapter, O(), I2)
        self.assertEqual(service.getAdapter(o, I1), o)

    def test_queryAdapter_and_getAdapter(self):
        service = self._service

        sm = traverse(self.rootFolder, '++etc++site')

        registration_manager = traverse(sm, 'default').getRegistrationManager()
        registration = Registration()
        name = registration_manager.addRegistration(registration)
        registration = traverse(registration_manager, name)

        class O:
            implements(I1)

        registration.factory = A

        registry = service.createRegistrationsFor(registration)
        registry.register(registration)
        registry.activate(registration)

        o = O()

        for m in 'queryAdapter', 'getAdapter':
            for r in I1, I1E:
                for p in I2B, I2:
                    o = O()
                    directlyProvides(o, r)

                    adapter = getattr(service, m)(o, p,)
                    self.assertEqual(adapter.__class__, A)
                    self.assertEqual(adapter.context, o)

            self.assertEqual(getattr(service, m)(o, I1), o)

        self.assertEqual(service.queryAdapter(o, I3), None)
        self.assertEqual(service.queryAdapter(o, I3, 42), 42)
        self.assertRaises(ComponentLookupError, service.getAdapter, O(), I3)

    def test_getAdapter_with_name(self):
        # The same as above, but with a named adapter
        service = self._service

        sm = traverse(self.rootFolder, '++etc++site')

        registration_manager = traverse(sm, 'default').getRegistrationManager()
        registration = Registration()
        registration.adapterName = u"Yatta!"
        key = registration_manager.addRegistration(registration)
        registration = traverse(registration_manager, key)

        class O:
            implements(I1)

        registration.factory = A

        registry = service.createRegistrationsFor(registration)
        registry.register(registration)
        registry.activate(registration)

        o = O()

        for r in I1, I1E:
            for p in I2B, I2:
                o = O()
                directlyProvides(o, r)

                adapter = service.getNamedAdapter(o, p, u"Yatta!")
                self.assertEqual(adapter.__class__, A)
                self.assertEqual(adapter.context, o)

        self.assertRaises(ComponentLookupError, service.getNamedAdapter,
                          o, I1, u"Yatta!")

        for r in I1, I1E:
            for p in I2B, I2:
                o = O()
                directlyProvides(o, r)

                adapter = service.queryNamedAdapter(o, p, u"Yatta!")
                self.assertEqual(adapter.__class__, A)
                self.assertEqual(adapter.context, o)

        self.assertEqual(service.queryNamedAdapter(o, I1, u"Yatta!"), None)

        self.assertRaises(ComponentLookupError, service.getNamedAdapter,
                          O(), I3, "Yatta!")
        self.assertEqual(service.queryNamedAdapter(o, I3, u"Yatta!"), None)
        self.assertEqual(service.queryNamedAdapter(o, I3, u"Yatta!", 42), 42)

    def test_queryAdapter_delegation(self):
        service = self._service

        sm = traverse(self.rootFolder, '++etc++site')

        registration_manager = traverse(sm, 'default').getRegistrationManager()
        registration = Registration()
        name = registration_manager.addRegistration(registration)
        registration = traverse(registration_manager, name)

        class O:
            implements(I1)

        registration.factory = A

        registry = service.createRegistrationsFor(registration)
        registry.register(registration)
        registry.activate(registration)

        o = O()

        class A2(A): pass

        provideAdapter(I1, I4, A2)

        adapter = service.queryAdapter(o, I4)
        self.assertEqual(adapter.__class__, A2)
        self.assertEqual(adapter.context, o)

    def test_queryAdapter_delegation_w_no_adapters_locally(self):
        service = self._service

        class O:
            implements(I1)

        o = O()

        class A2(A): pass

        provideAdapter(I1, I4, A2)

        adapter = service.queryAdapter(o, I4)
        self.assertEqual(adapter.__class__, A2)
        self.assertEqual(adapter.context, o)

    def test_getRegisteredMatching(self):
        self.test_queryAdapter_and_getAdapter()
        registry = self._service.queryRegistrations(I1, I2, '')

        for args in ((), (I1E, ), (None, I2), (I1E, I2), ):
            r = self._service.getRegisteredMatching(*args)
            self.assertEqual(list(r), [(I1, I2, registry)])

class ModuleFinder:

    def resolve(self, name):
        if name == "Foo.Bar.A":
            return A
        raise ImportError(name)

class TestAdapterRegistration(TestCase):

    def test_getAdapter(self):
        folder = ModuleFinder()
        folder = contained(folder, folder)

        registration = contained(
            AdapterRegistration(I1, I2, "Foo.Bar.A", "adapter"),
            folder,
            )

        c = C()
        adapter = registration.getAdapter(c)
        self.assertEqual(adapter.__class__, A)
        self.assertEqual(adapter.context, c)
        self.assertEqual(registration.forInterface, I1)
        self.assertEqual(registration.providedInterface, I2)

def test_suite():
    return TestSuite((
        makeSuite(TestAdapterService),
        makeSuite(TestAdapterRegistration),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
