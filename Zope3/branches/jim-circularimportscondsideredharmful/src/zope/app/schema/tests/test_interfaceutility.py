##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Utility service tests

$Id$
"""
import unittest
from zope.app.tests import setup
from zope.app.site.tests import placefulsetup
from zope.app import utility
from zope.app import zapi
from zope.app.servicenames import Utilities
from zope.app.component.interface import getInterface, searchInterface
from zope.interface import Interface, implements
from zope.app.container.contained import Contained
from zope.component import getService
from zope.component.exceptions import ComponentLookupError
from zope.app.traversing.api import traverse
from zope.app.registration.interfaces import IRegistrationStack
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.registration.interfaces import IRegistered
from zope.app.utility.interfaces import ILocalUtility
from zope.app.dependable.interfaces import IDependable
from zope.app.tests import setup
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IInterface
from zope.interface import Interface

class IBaz(Interface): pass

class Baz:
    # We implement IRegistered and IDependable directly to
    # depend as little  as possible on other infrastructure.
    implements(IBaz, ILocalUtility, IRegistered, IDependable)

    def __init__(self, name):
        self.name = name
        self._usages = []
        self._dependents = []

    def foo(self):
        return 'foo ' + self.name

    def addUsage(self, location):
        "See zope.app.registration.interfaces.IRegistered"
        if location not in self._usages:
            self._usages.append(location)

    def removeUsage(self, location):
        "See zope.app.registration.interfaces.IRegistered"
        self._usages.remove(location)

    def usages(self):
        "See zope.app.registration.interfaces.IRegistered"
        return self._usages

    def addDependent(self, location):
        "See zope.app.dependable.interfaces.IDependable"
        if location not in self._dependents:
            self._dependents.append(location)

    def removeDependent(self, location):
        "See zope.app.dependable.interfaces.IDependable"
        self._dependents.remove(location)

    def dependents(self):
        "See zope.app.dependable.interfaces.IDependable"
        return self._dependents

class Foo(InterfaceClass, Baz, Contained):

    def __init__(self, name):
        InterfaceClass.__init__(self, name, (Interface,))
        Baz.__init__(self, name)

class Bar(Foo): pass

class TestInterfaceUtility(placefulsetup.PlacefulSetup, unittest.TestCase):

    def setUp(self):
        sm = placefulsetup.PlacefulSetup.setUp(self, site=True)
        setup.addService(sm, Utilities,
                         utility.LocalUtilityService())

    def test_getLocalInterface_delegates_to_globalUtility(self):
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, Bar("blob"),
                                            name="blob")
        utilityService.provideUtility(IBaz, Baz("global baz"))
        utilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        self.assertEqual(getInterface(None, "bob").__class__, Foo)
        self.assertEqual(getInterface(None, "blob").__class__, Bar)

    def test_localInterfaceitems_filters_accordingly(self):
        bar = Bar("global")
        baz = Baz("global baz")
        foo = Foo("global bob")

        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, foo,
                                            name="bob")
        utilityService.provideUtility(IInterface, bar)
        utilityService.provideUtility(IBaz, baz)

        ifaces = searchInterface(None)
        self.assert_(len(ifaces), 2)
        for pair in [(foo), (bar)]:
            self.assert_(pair in ifaces)

        iface_utilities = utilityService.getUtilitiesFor(IInterface)
        ifaces = [iface for (name, iface) in iface_utilities]

        self.assert_(len(ifaces), 2)
        for pair in [(foo), (bar)]:
            self.assert_(pair in ifaces)

        for pair in [(foo), (bar)]:
            self.assert_(pair in ifaces)

    def test_localInterfaceitems_filters_only_interfaces(self):
        bar = Bar("global")
        baz = Baz("global baz")
        foo = Foo("global bob")
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, foo,
                                            name="bob")
        utilityService.provideUtility(ILocalUtility, bar)
        utilityService.provideUtility(IBaz, baz)

        iface_utilities = utilityService.getUtilitiesFor(IInterface)
        ifaces = [iface for (name, iface) in iface_utilities]
        self.assertEqual(ifaces, [(foo)])

        iface_utilities = utilityService.getUtilitiesFor(ILocalUtility)
        ifaces = [iface for (name, iface) in iface_utilities]
        self.assertEqual(ifaces, [(bar)])

        iface_utilities = utilityService.getUtilitiesFor(IBaz)
        ifaces = [iface for (name, iface) in iface_utilities]
        self.assertEqual(ifaces, [(baz)])

    def test_getLocalInterface_raisesComponentLookupError(self):
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, Foo("global"))
        utilityService.provideUtility(IBaz, Baz("global baz"))
        utilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        self.assertRaises(ComponentLookupError,
                          getInterface, None, "bobesponja")

    def test_globalsearchInterface_delegates_to_globalUtility(self):
        foo = Foo("global bob")
        bar = Bar("global")
        baz = Baz("global baz")
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, bar)
        utilityService.provideUtility(IBaz, baz)
        utilityService.provideUtility(IInterface, foo,
                                            name="bob")

        self.assertEqual(searchInterface(None, search_string="bob"),
                         [foo])

    def test_localsearchInterface_delegates_to_globalUtility(self):
        foo = Foo("global bob")
        bar = Bar("global")
        baz = Baz("global baz")
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, bar)
        utilityService.provideUtility(IBaz, baz)
        utilityService.provideUtility(IInterface, foo,
                                            name="bob")

        self.assertEqual(searchInterface(None, search_string="bob"),
                         [foo])

    def test_queryUtility_delegates_to_global(self):
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, Foo("global"))
        utilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        utility_service = getService(Utilities, self.rootFolder)
        self.assert_(utility_service != utilityService)

        self.assertEqual(utility_service.queryUtility(IInterface).foo(),
                         "foo global")
        self.assertEqual(
            utility_service.queryUtility(IInterface, "bob").foo(),
            "foo global bob")

    def test_getUtility_delegates_to_global(self):
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, Foo("global"))
        utilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        utility_service = getService(Utilities, self.rootFolder)
        self.assert_(utility_service != utilityService)

        self.assertEqual(utility_service.getUtility(IInterface).foo(),
                         "foo global")
        self.assertEqual(
            utility_service.getUtility(IInterface, "bob").foo(),
            "foo global bob")


    def test_registrationsFor_methods(self):
        utilities = getService(Utilities, self.rootFolder)
        default = traverse(self.rootFolder, "++etc++site/default")
        default['foo'] = Foo("local")
        path = "/++etc++site/default/foo"

        for name in ('', 'bob'):
            registration = utility.UtilityRegistration(name, IInterface, path)
            self.assertEqual(utilities.queryRegistrationsFor(registration),
                             None)
            registery = utilities.createRegistrationsFor(registration)
            self.assert_(IRegistrationStack.providedBy(registery))
            self.assertEqual(utilities.queryRegistrationsFor(registration),
                             registery)


    def test_local_utilities(self):
        utilityService = zapi.getGlobalService(zapi.servicenames.Utilities)
        utilityService.provideUtility(IInterface, Foo("global"))
        utilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        utilities = getService(Utilities, self.rootFolder)
        default = traverse(self.rootFolder, "++etc++site/default")
        default['foo'] = Foo("local")
        path = "/++etc++site/default/foo"
        cm = default.getRegistrationManager()

        for name in ('', 'bob'):
            registration = utility.UtilityRegistration(name, IInterface, path)
            cname = cm.addRegistration(registration)
            registration = traverse(cm, cname)

            gout = name and "foo global "+name or "foo global"

            self.assertEqual(utilities.getUtility(IInterface, name).foo(),
                             gout)

            registration.status = ActiveStatus

            self.assertEqual(utilities.getUtility(IInterface, name).foo(),
                             "foo local")

            registration.status = RegisteredStatus

            self.assertEqual(utilities.getUtility(IInterface, name).foo(), gout)


def test_suite():
    return unittest.makeSuite(TestInterfaceUtility)

if __name__ == '__main__':
    unittest.main()
