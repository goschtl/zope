##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Utility service tests

XXX longer description goes here.

$Id: test_interfaceutility.py,v 1.8 2004/03/05 22:09:21 jim Exp $
"""

import unittest
from zope.app.tests import setup
from zope.app.services.tests import placefulsetup
from zope.app.services import utility
from zope.app.services.servicenames import Utilities
from zope.component.utility import utilityService as globalUtilityService
from zope.app.component.interface import getInterface, searchInterface
from zope.interface import Interface, implements
from zope.app.container.contained import Contained
from zope.component import getService
from zope.component.exceptions import ComponentLookupError
from zope.app.traversing import traverse
from zope.app.interfaces.services.registration import IRegistrationStack
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.utility import ILocalUtility
from zope.app.interfaces.services.registration import IRegistered
from zope.app.interfaces.dependable import IDependable
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
        "See zope.app.interfaces.services.registration.IRegistered"
        if location not in self._usages:
            self._usages.append(location)

    def removeUsage(self, location):
        "See zope.app.interfaces.services.registration.IRegistered"
        self._usages.remove(location)

    def usages(self):
        "See zope.app.interfaces.services.registration.IRegistered"
        return self._usages

    def addDependent(self, location):
        "See zope.app.interfaces.dependable.IDependable"
        if location not in self._dependents:
            self._dependents.append(location)

    def removeDependent(self, location):
        "See zope.app.interfaces.dependable.IDependable"
        self._dependents.remove(location)

    def dependents(self):
        "See zope.app.interfaces.dependable.IDependable"
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
        globalUtilityService.provideUtility(IInterface, Bar("blob"),
                                            name="blob")
        globalUtilityService.provideUtility(IBaz, Baz("global baz"))
        globalUtilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        self.assertEqual(getInterface(None, "bob").__class__, Foo)
        self.assertEqual(getInterface(None, "blob").__class__, Bar)

    def test_localInterfaceitems_filters_accordingly(self):
        bar = Bar("global")
        baz = Baz("global baz")
        foo = Foo("global bob")

        globalUtilityService.provideUtility(IInterface, foo,
                                            name="bob")
        globalUtilityService.provideUtility(IInterface, bar)
        globalUtilityService.provideUtility(IBaz, baz)

        ifaces = searchInterface(None)
        self.assert_(len(ifaces), 2)
        for pair in [(foo), (bar)]:
            self.assert_(pair in ifaces)

        iface_utilities = globalUtilityService.getUtilitiesFor(IInterface)
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
        globalUtilityService.provideUtility(IInterface, foo,
                                            name="bob")
        globalUtilityService.provideUtility(ILocalUtility, bar)
        globalUtilityService.provideUtility(IBaz, baz)

        iface_utilities = globalUtilityService.getUtilitiesFor(IInterface)
        ifaces = [iface for (name, iface) in iface_utilities]
        self.assertEqual(ifaces, [(foo)])

        iface_utilities = globalUtilityService.getUtilitiesFor(ILocalUtility)
        ifaces = [iface for (name, iface) in iface_utilities]
        self.assertEqual(ifaces, [(bar)])

        iface_utilities = globalUtilityService.getUtilitiesFor(IBaz)
        ifaces = [iface for (name, iface) in iface_utilities]
        self.assertEqual(ifaces, [(baz)])

    def test_getLocalInterface_raisesComponentLookupError(self):
        globalUtilityService.provideUtility(IInterface, Foo("global"))
        globalUtilityService.provideUtility(IBaz, Baz("global baz"))
        globalUtilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        self.assertRaises(ComponentLookupError,
                          getInterface, None, "bobesponja")

    def test_globalsearchInterface_delegates_to_globalUtility(self):
        foo = Foo("global bob")
        bar = Bar("global")
        baz = Baz("global baz")
        globalUtilityService.provideUtility(IInterface, bar)
        globalUtilityService.provideUtility(IBaz, baz)
        globalUtilityService.provideUtility(IInterface, foo,
                                            name="bob")

        self.assertEqual(searchInterface(None, search_string="bob"),
                         [foo])

    def test_localsearchInterface_delegates_to_globalUtility(self):
        foo = Foo("global bob")
        bar = Bar("global")
        baz = Baz("global baz")
        globalUtilityService.provideUtility(IInterface, bar)
        globalUtilityService.provideUtility(IBaz, baz)
        globalUtilityService.provideUtility(IInterface, foo,
                                            name="bob")

        self.assertEqual(searchInterface(None, search_string="bob"),
                         [foo])

    def test_queryUtility_delegates_to_global(self):
        globalUtilityService.provideUtility(IInterface, Foo("global"))
        globalUtilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        utility_service = getService(self.rootFolder, Utilities)
        self.assert_(utility_service != globalUtilityService)

        self.assertEqual(utility_service.queryUtility(IInterface).foo(),
                         "foo global")
        self.assertEqual(
            utility_service.queryUtility(IInterface, name="bob").foo(),
            "foo global bob")

    def test_getUtility_delegates_to_global(self):
        globalUtilityService.provideUtility(IInterface, Foo("global"))
        globalUtilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        utility_service = getService(self.rootFolder, Utilities)
        self.assert_(utility_service != globalUtilityService)

        self.assertEqual(utility_service.getUtility(IInterface).foo(),
                         "foo global")
        self.assertEqual(
            utility_service.getUtility(IInterface, name="bob").foo(),
            "foo global bob")


    def test_registrationsFor_methods(self):
        utilities = getService(self.rootFolder, Utilities)
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
        globalUtilityService.provideUtility(IInterface, Foo("global"))
        globalUtilityService.provideUtility(IInterface, Foo("global bob"),
                                            name="bob")

        utilities = getService(self.rootFolder, Utilities)
        default = traverse(self.rootFolder, "++etc++site/default")
        default['foo'] = Foo("local")
        path = "/++etc++site/default/foo"
        cm = default.getRegistrationManager()

        for name in ('', 'bob'):
            registration = utility.UtilityRegistration(name, IInterface, path)
            cname = cm.addRegistration(registration)
            registration = traverse(cm, cname)

            gout = name and "foo global "+name or "foo global"

            self.assertEqual(utilities.getUtility(IInterface, name=name).foo(),
                             gout)

            registration.status = ActiveStatus

            self.assertEqual(utilities.getUtility(IInterface, name=name).foo(),
                             "foo local")

            registration.status = RegisteredStatus

            self.assertEqual(utilities.getUtility(IInterface, name=name).foo(),
                             gout)

    def test_getRegisteredMatching(self):
        self.test_local_utilities()
        utilities = getService(self.rootFolder, Utilities)
        r = list(utilities.getRegisteredMatching())
        r.sort()
        path = "/++etc++site/default/foo"
        cr1 = utilities.queryRegistrationsFor(
            utility.UtilityRegistration("", IInterface, path))
        cr2 = utilities.queryRegistrationsFor(
            utility.UtilityRegistration("bob", IInterface, path))
        self.assertEqual(r, [(IInterface, "", cr1), (IInterface, "bob", cr2)])
        self.assertEqual(r[0][2].__parent__, utilities)
        self.assertEqual(r[1][2].__parent__, utilities)
        # Now tescvt that an empty registry doesn't show up
        for cd in cr1.info(): # Remove everything from cr1
            cd['registration'].status = UnregisteredStatus
        self.assertEqual(bool(cr1), False)
        r = list(utilities.getRegisteredMatching())
        self.assertEqual(r, [(IInterface, "bob", cr2)])


def test_suite():
    return unittest.makeSuite(TestInterfaceUtility)

if __name__ == '__main__':
    unittest.main()
