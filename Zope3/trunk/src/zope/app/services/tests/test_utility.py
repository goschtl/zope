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

$Id: test_utility.py,v 1.5 2003/05/01 19:35:35 faassen Exp $
"""

import unittest
from zope.app.services.tests import placefulsetup
from zope.app.services import utility
from zope.component.utility import utilityService as globalUtilityService
from zope.interface import Interface
from zope.component import getService
from zope.component.exceptions import ComponentLookupError
from zope.app.traversing import traverse
from zope.app.interfaces.services.configuration import IConfigurationRegistry
from zope.app.interfaces.services.configuration \
     import Active, Registered, Unregistered
from zope.app.interfaces.services.utility import ILocalUtility
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.interfaces.dependable import IDependable
from zope.proxy.context import getWrapperContainer

class IFo(Interface): pass

class IFoo(IFo):
    def foo(self): pass

class IBar(Interface): pass


class Foo:
    # We implement IUseConfiguration and IDependable directly to
    # depend as little  as possible on other infrastructure.
    __implements__ = IFoo, ILocalUtility, IUseConfiguration, IDependable

    def __init__(self, name):
        self.name = name
        self._usages = []
        self._dependents = []
        
    def foo(self):
        return 'foo ' + self.name
    
    def addUsage(self, location):
        "See zope.app.interfaces.services.configuration.IUseConfiguration"
        if location not in self._usages:
            self._usages.append(location)
    
    def removeUsage(self, location):
        "See zope.app.interfaces.services.configuration.IUseConfiguration"
        self._usages.remove(location)
            
    def usages(self):
        "See zope.app.interfaces.services.configuration.IUseConfiguration"
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

class TestUtilityService(placefulsetup.PlacefulSetup, unittest.TestCase):

    def setUp(self):
        placefulsetup.PlacefulSetup.setUp(self)
        self.buildFolders()
        sm = placefulsetup.createServiceManager(self.rootFolder)
        placefulsetup.addService(sm, "Utilities",
                                 utility.LocalUtilityService())

    def test_queryUtility_delegates_to_global(self):
        globalUtilityService.provideUtility(IFoo, Foo("global"))
        globalUtilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utility_service = getService(self.rootFolder, "Utilities")
        self.assert_(utility_service != globalUtilityService)

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
        globalUtilityService.provideUtility(IFoo, Foo("global"))
        globalUtilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utility_service = getService(self.rootFolder, "Utilities")
        self.assert_(utility_service != globalUtilityService)

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


    def test_configurationsFor_methods(self):
        utilities = getService(self.rootFolder, "Utilities")
        default = traverse(self.rootFolder, "++etc++Services/default")
        default.setObject('foo', Foo("local"))
        path = "/++etc++Services/default/foo"

        for name in ('', 'bob'):
            configuration = utility.UtilityConfiguration(name, IFoo, path)
            self.assertEqual(utilities.queryConfigurationsFor(configuration),
                             None)
            registery = utilities.createConfigurationsFor(configuration)
            self.assert_(IConfigurationRegistry.isImplementedBy(registery))
            self.assertEqual(utilities.queryConfigurationsFor(configuration),
                             registery)


    def test_local_utilities(self):
        globalUtilityService.provideUtility(IFoo, Foo("global"))
        globalUtilityService.provideUtility(IFoo, Foo("global bob"),
                                            name="bob")

        utilities = getService(self.rootFolder, "Utilities")
        default = traverse(self.rootFolder, "++etc++Services/default")
        default.setObject('foo', Foo("local"))
        path = "/++etc++Services/default/foo"
        cm = default.getConfigurationManager()

        for name in ('', 'bob'):
            configuration = utility.UtilityConfiguration(name, IFoo, path)
            cname = cm.setObject('', configuration)
            configuration = traverse(cm, cname)

            gout = name and "foo global "+name or "foo global"

            self.assertEqual(utilities.getUtility(IFoo, name=name).foo(), gout)

            configuration.status = Active

            self.assertEqual(utilities.getUtility(IFoo, name=name).foo(),
                             "foo local")

            configuration.status = Registered

            self.assertEqual(utilities.getUtility(IFoo, name=name).foo(), gout)

    def test_getRegisteredMatching(self):
        self.test_local_utilities()
        utilities = getService(self.rootFolder, "Utilities")
        r = list(utilities.getRegisteredMatching())
        r.sort()
        path = "/++etc++Services/default/foo"
        cr1 = utilities.queryConfigurationsFor(
            utility.UtilityConfiguration("", IFoo, path))
        cr2 = utilities.queryConfigurationsFor(
            utility.UtilityConfiguration("bob", IFoo, path))
        self.assertEqual(r, [(IFoo, "", cr1), (IFoo, "bob", cr2)])
        self.assertEqual(getWrapperContainer(r[0][2]), utilities)
        self.assertEqual(getWrapperContainer(r[1][2]), utilities)
        # Now test that an empty registry doesn't show up
        for cd in cr1.info(): # Remove everything from cr1
            cd['configuration'].status = Unregistered
        self.assertEqual(bool(cr1), False)
        r = list(utilities.getRegisteredMatching())
        self.assertEqual(r, [(IFoo, "bob", cr2)])


def test_suite():
    return unittest.makeSuite(TestUtilityService)


if __name__ == '__main__':
    unittest.main()
