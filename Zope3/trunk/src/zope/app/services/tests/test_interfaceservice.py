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
import unittest

from zope.component.exceptions import ComponentLookupError
from zope.interface import Interface
from zope.interface.verify import verifyObject

from zope.app.component.globalinterfaceservice \
     import interfaceService as globalService
from zope.app.interfaces.component import IInterfaceService
from zope.app.services.interface import LocalInterfaceService
from zope.app.services.servicenames import Interfaces
from zope.app.tests import setup


class B(Interface):
    pass

class I(Interface):
    """bah blah."""

class I2(B):
    """eek"""

class I3(B):

    def one():
        """method one"""

    def two():
        """method two"""

class Test(unittest.TestCase):
    """Test Interface for LocalInterfaceService instance."""

    def setUp(self):
        setup.placefulSetUp()

    def tearDown(self):
        setup.placefulTearDown()
        
    def testInterfaceVerification(self):
        verifyObject(IInterfaceService, LocalInterfaceService())

    def testDelegationToGlobalInterfaceService(self):
        rootFolder = setup.buildSampleFolderTree()
        mgr = setup.createServiceManager(rootFolder)
        
        service = setup.addService(mgr, Interfaces, LocalInterfaceService())

        self.assertRaises(ComponentLookupError,
                          service.getInterface, "Foo.Bar")
        self.assertEqual(service.queryInterface("Foo.Bar"), None)
        self.assertEqual(service.queryInterface("Foo.Bar", 42), 42)
        self.failIf(service.searchInterface(""))

        globalService.provideInterface("Foo.Bar", I)

        self.assertEqual(service.getInterface("Foo.Bar"), I)
        self.assertEqual(service.queryInterface("Foo.Bar"), I)
        self.assertEqual(list(service.searchInterface("")), [I])
        self.assertEqual(list(service.searchInterface(base=B)), [])

        globalService.provideInterface("Foo.Baz", I2)

        result = list(service.searchInterface(""))
        result.sort()
        self.assertEqual(result, [I, I2])

        self.assertEqual(list(service.searchInterface("I2")), [I2])
        self.assertEqual(list(service.searchInterface("eek")), [I2])

        self.assertEqual(list(service.searchInterfaceIds("I2")), ["Foo.Baz"])
        self.assertEqual(list(service.searchInterfaceIds("eek")), ["Foo.Baz"])

        globalService.provideInterface("Foo.Bus", I3)
        self.assertEqual(list(service.searchInterface("two")), [I3])
        self.assertEqual(list(service.searchInterface("two", base=B)), [I3])

        r = list(service.searchInterface(base=B))
        r.sort()
        self.assertEqual(r, [I2, I3])

def test_suite():
    return unittest.makeSuite(Test)
