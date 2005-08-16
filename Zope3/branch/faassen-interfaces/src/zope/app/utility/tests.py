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

$Id: tests.py,v 1.8 2004/04/24 23:20:26 srichter Exp $
"""
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.app.tests import setup
from zope.app.site.tests import placefulsetup
from zope.app import utility, zapi
from zope.interface import Interface, implements
from zope.component import getService
from zope.component.exceptions import ComponentLookupError
from zope.app.traversing import traverse
from zope.app.registration.interfaces import IRegistrationStack
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.registration.interfaces import IRegistered
from zope.app.utility.interfaces import ILocalUtility
from zope.app.dependable.interfaces import IDependable
from zope.app.tests import setup

class IFo(Interface): pass

class IFoo(IFo):
    def foo(self): pass

class IBar(Interface): pass


class Foo:
    # We implement IRegistered and IDependable directly to
    # depend as little  as possible on other infrastructure.
    __name__ = __parent__ = None
    implements(IFoo, ILocalUtility, IRegistered, IDependable)
    
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

class TestUtilityService(placefulsetup.PlacefulSetup, unittest.TestCase):

    def setUp(self):
        sm = placefulsetup.PlacefulSetup.setUp(self, site=True)
        setup.addService(sm, zapi.servicenames.Utilities,
                         utility.LocalUtilityService())

    def test_queryUtility_delegates_to_global(self):
        utilityService = zapi.getService(None, zapi.servicenames.Utilities)
        utilityService.provideUtility(IFoo, Foo("global"))
        utilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utility_service = getService(self.rootFolder, "Utilities")

        # We changed the root (base) service. This doesn't normally
        # occur.  We have to notify the local service that the base
        # has changes:
        utility_service.baseChanged()
        
        self.assert_(utility_service != utilityService)

        self.assertEqual(utility_service.queryUtility(IFoo).foo(),
                         "foo global")
        self.assertEqual(utility_service.queryUtility(IFoo, name="bob").foo(),
                         "foo global bob")
        self.assertEqual(utility_service.queryUtility(IFo).foo(),
                         "foo global")
        self.assertEqual(utility_service.queryUtility(IFo, name="bob").foo(),
                         "foo global bob")

        self.assertEqual(utility_service.queryUtility(IBar), None)
        self.assertEqual(utility_service.queryUtility(IBar, name="bob"), None)
        self.assertEqual(utility_service.queryUtility(IFoo, name="rob"), None)

    def test_getUtility_delegates_to_global(self):
        utilityService = zapi.getService(None, zapi.servicenames.Utilities)
        utilityService.provideUtility(IFoo, Foo("global"))
        utilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utility_service = getService(self.rootFolder, "Utilities")
        self.assert_(utility_service != utilityService)

        self.assertEqual(utility_service.getUtility(IFoo).foo(),
                         "foo global")
        self.assertEqual(utility_service.getUtility(IFoo, name="bob").foo(),
                         "foo global bob")
        self.assertEqual(utility_service.getUtility(IFo).foo(),
                         "foo global")
        self.assertEqual(utility_service.getUtility(IFo, name="bob").foo(),
                         "foo global bob")


        self.assertRaises(ComponentLookupError,
                          utility_service.getUtility, IBar)
        self.assertRaises(ComponentLookupError,
                          utility_service.getUtility, IBar, name='bob')
        self.assertRaises(ComponentLookupError,
                          utility_service.getUtility, IFoo, name='rob')


    def test_registrationsFor_methods(self):
        utilities = getService(self.rootFolder, "Utilities")
        default = traverse(self.rootFolder, "++etc++site/default")
        default['foo'] = Foo("local")
        path = "/++etc++site/default/foo"

        for name in ('', 'bob'):
            registration = utility.UtilityRegistration(name, IFoo, path)
            self.assertEqual(utilities.queryRegistrationsFor(registration),
                             None)
            registery = utilities.createRegistrationsFor(registration)
            self.assert_(IRegistrationStack.providedBy(registery))
            self.assertEqual(utilities.queryRegistrationsFor(registration),
                             registery)


    def test_local_utilities(self):
        utilityService = zapi.getService(None, zapi.servicenames.Utilities)
        utilityService.provideUtility(IFoo, Foo("global"))
        utilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utilities = getService(self.rootFolder, "Utilities")

        # We changed the root (base) service. This doesn't normally
        # occur.  We have to notify the local service that the base
        # has changes:
        utilities.baseChanged()

        default = traverse(self.rootFolder, "++etc++site/default")
        default['foo'] = Foo("local")
        path = "/++etc++site/default/foo"
        cm = default.getRegistrationManager()

        for name in ('', 'bob'):
            registration = utility.UtilityRegistration(name, IFoo, path)
            cname = cm.addRegistration(registration)
            registration = traverse(cm, cname)

            gout = name and "foo global "+name or "foo global"

            self.assertEqual(utilities.getUtility(IFoo, name=name).foo(), gout)

            registration.status = ActiveStatus

            self.assertEqual(utilities.getUtility(IFoo, name=name).foo(),
                             "foo local")

            registration.status = RegisteredStatus

            self.assertEqual(utilities.getUtility(IFoo, name=name).foo(), gout)


    def test_local_overrides(self):
        # Make sure that a local utility service can override another
        sm1 = zapi.traverse(self.rootFolder, "++etc++site")
        setup.addUtility(sm1, 'u1', IFoo, Foo('u1'))
        setup.addUtility(sm1, 'u2', IFoo, Foo('u2'))
        sm2 = self.makeSite('folder1')
        setup.addService(sm2, zapi.servicenames.Utilities,
                         utility.LocalUtilityService())
        setup.addUtility(sm2, 'u2', IFoo, Foo('u22'))

        # Make sure we acquire:
        self.assertEqual(zapi.getUtility(sm2, IFoo, 'u1').name, 'u1')

        # Make sure we override:
        self.assertEqual(zapi.getUtility(sm2, IFoo, 'u2').name, 'u22')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtilityService),
        DocTestSuite('zope.app.utility.vocabulary',
                     setUp=setup.placelessSetUp,
                     tearDown=setup.placelessTearDown)
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
