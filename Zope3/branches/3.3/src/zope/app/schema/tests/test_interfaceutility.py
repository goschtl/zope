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
"""Interfaces as Utilities tests

$Id$
"""
import unittest
import zope.component
from zope.interface import Interface, implements
from zope.interface.interface import InterfaceClass
from zope.interface.interfaces import IInterface
from zope.component.interfaces import ComponentLookupError
from zope.component.interface import getInterface, searchInterface
from zope.traversing.api import traverse

from zope.app.component.testing import PlacefulSetup
from zope.app.container.contained import Contained
from zope.app.dependable.interfaces import IDependable
from zope.app.testing import setup

class IBaz(Interface): pass

class Baz(object):
    # We implement IDependable directly to
    # depend as little  as possible on other infrastructure.
    implements(IBaz, IDependable)

    def __init__(self, name):
        self.name = name
        self._dependents = []

    def foo(self):
        return 'foo ' + self.name

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

class TestInterfaceUtility(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        sm = PlacefulSetup.setUp(self, site=True)

    def test_getLocalInterface_delegates_to_globalUtility(self):
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(Bar("blob"), IInterface, name="blob")
        gsm.registerUtility(Baz("global baz"), IBaz)
        gsm.registerUtility(Foo("global bob"), IInterface, name="bob")

        self.assertEqual(getInterface(None, "bob").__class__, Foo)
        self.assertEqual(getInterface(None, "blob").__class__, Bar)

    def test_localInterfaceitems_filters_accordingly(self):
        bar = Bar("global")
        baz = Baz("global baz")
        foo = Foo("global bob")

        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(foo, IInterface, name="bob")
        gsm.registerUtility(bar, IInterface)
        gsm.registerUtility(baz, IBaz)

        ifaces = searchInterface(None)
        self.assert_(len(ifaces), 2)
        for pair in [(foo), (bar)]:
            self.assert_(pair in ifaces)

        iface_utilities = gsm.getUtilitiesFor(IInterface)
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
        gsm = zope.component.getGlobalSiteManager()

        gsm.registerUtility(foo, IInterface, name="bob")
        gsm.registerUtility(baz, IBaz)

        iface_utilities = gsm.getUtilitiesFor(IInterface)
        ifaces = [iface for (name, iface) in iface_utilities]
        self.assertEqual(ifaces, [(foo)])

        iface_utilities = gsm.getUtilitiesFor(IBaz)
        ifaces = [iface for (name, iface) in iface_utilities]
        self.assertEqual(ifaces, [(baz)])

    def test_getLocalInterface_raisesComponentLookupError(self):
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(Foo("global"), Interface)
        gsm.registerUtility(Baz("global baz"), IBaz)
        gsm.registerUtility(Foo("global bob"), IInterface, name="bob")

        self.assertRaises(ComponentLookupError,
                          getInterface, None, "bobesponja")

    def test_globalsearchInterface_delegates_to_globalUtility(self):
        foo = Foo("global bob")
        bar = Bar("global")
        baz = Baz("global baz")
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(foo, IInterface, name="bob")
        gsm.registerUtility(bar, IInterface)
        gsm.registerUtility(baz, IBaz)

        self.assertEqual(searchInterface(None, search_string="bob"),
                         [foo])

    def test_localsearchInterface_delegates_to_globalUtility(self):
        # Same test as above!
        foo = Foo("global bob")
        bar = Bar("global")
        baz = Baz("global baz")
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(foo, IInterface, name="bob")
        gsm.registerUtility(bar, IInterface)
        gsm.registerUtility(baz, IBaz)

        self.assertEqual(searchInterface(None, search_string="bob"),
                         [foo])

    def test_query_get_Utility_delegates_to_global(self):
        zope.component.provideUtility(Foo("global"), IInterface)
        zope.component.provideUtility(Foo("global bob"), IInterface,
                                      name="bob")

        gsm = zope.component.getGlobalSiteManager()
        sm = zope.component.getSiteManager(self.rootFolder)
        self.assert_(gsm != sm)

        # If queryUtility works on the site manager, getUtility in zapi must
        # also work.
        self.assertEqual(sm.queryUtility(IInterface).foo(), "foo global")
        self.assertEqual(sm.queryUtility(IInterface, "bob").foo(),
                         "foo global bob")

    def test_local_utilities(self):
        gsm = zope.component.getGlobalSiteManager()
        gsm.registerUtility(Foo("global"), IInterface)
        gsm.registerUtility(Foo("global bob"), IInterface, name="bob")

        sm = zope.component.getSiteManager(self.rootFolder)
        default = traverse(self.rootFolder, "++etc++site/default")
        default['foo'] = Foo("local")
        foo = default['foo']

        for name in ('', 'bob'):
            gout = name and "foo global "+name or "foo global"
            self.assertEqual(sm.queryUtility(IInterface, name).foo(), gout)
            sm.registerUtility(foo, IInterface, name)
            self.assertEqual(
                sm.queryUtility(IInterface, name).foo(), "foo local")
            sm.unregisterUtility(foo, IInterface, name)
            self.assertEqual(sm.queryUtility(IInterface, name).foo(), gout)


def test_suite():
    return unittest.makeSuite(TestInterfaceUtility)

if __name__ == '__main__':
    unittest.main()
