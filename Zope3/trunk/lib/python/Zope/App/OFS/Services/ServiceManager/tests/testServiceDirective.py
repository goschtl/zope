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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: testServiceDirective.py,v 1.1 2002/07/11 18:21:33 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.ComponentArchitecture import getService
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Security.Proxy import Proxy, getChecker
from Zope.App.Traversing.ITraversable import ITraversable
from Interface import Interface
from Zope.App.OFS.Services.ServiceManager.ServiceDirective \
     import ServiceDirective
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup

from Zope.App.Traversing.IPhysicallyLocatable import IPhysicallyLocatable
from Zope.App.Traversing.IContainmentRoot import IContainmentRoot
from Zope.App.Traversing.PhysicalLocationAdapters \
     import WrapperPhysicallyLocatable, RootPhysicallyLocatable

class IFoo(Interface):
    def f1(): pass
    def f2(): pass

class ServiceManager:
    __implements__ = ITraversable, IContainmentRoot
    
    def getInterfaceFor(self, name):
        return IFoo

    def traverse(self, name, *ignored):
        return getattr(self, name)

class Comp:
    __implements__ = IFoo

    def f1(self): return 1
    def f2(self): return 2
    def f3(self): return 3

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        adapterService=getService(None, "Adapters")
        
        adapterService.provideAdapter(
              None, IPhysicallyLocatable, WrapperPhysicallyLocatable)
        adapterService.provideAdapter(
              IContainmentRoot, IPhysicallyLocatable, RootPhysicallyLocatable)


    def test_getService(self):
        sm = ServiceManager()
        sm.C = Comp()
        dir = ServiceDirective('Foo', '/C', 'ppp')
        service = dir.getService(sm)
        self.assertEqual(type(service), Proxy)
        self.assertEqual(service.__class__, Comp)
        checker = getChecker(service)
        self.assertEqual(checker.permission_id('f1'), 'ppp')
        self.assertEqual(checker.permission_id('f2'), 'ppp')
        self.assertEqual(checker.permission_id('f3'), None)        

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
