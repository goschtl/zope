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
"""test utility service

XXX longer description goes here.

$Id: test_utilityservice.py,v 1.8 2003/12/19 16:53:21 mchandra Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.component import \
     getUtility, getUtilitiesFor, getService, queryUtility, getServiceManager
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Utilities
from zope.interface import Interface, implements

from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class IDummyService(Interface):
    pass

class DummyService:
    implements(IDummyService)

dummyService = DummyService()

class Test(TestCase, CleanUp):
    def setUp(self):
        CleanUp.setUp(self)
        sm=getServiceManager(None)
        defineService=sm.defineService
        provideService=sm.provideService
        from zope.component.interfaces import IUtilityService
        defineService('Utilities',IUtilityService)
        from zope.component.utility import utilityService
        provideService('Utilities', utilityService)

    def testGetUtility(self):
        us = getService(None, Utilities)
        self.assertRaises(
            ComponentLookupError, getUtility, None, IDummyService)
        us.provideUtility(IDummyService, dummyService)
        self.assertEqual(getUtility(None, IDummyService), dummyService)

    def testQueryUtility(self):
        us = getService(None, Utilities)
        self.assertEqual(queryUtility(None, IDummyService), None)
        self.assertEqual(queryUtility(None, IDummyService, self), self)
        us.provideUtility(IDummyService, dummyService)
        self.assertEqual(queryUtility(None, IDummyService), dummyService)

    def testgetUtilitiesFor(self):
        us = getService(None, Utilities)
        us.provideUtility(IDummyService, dummyService)
        conns = getUtilitiesFor(None, IDummyService)
        self.assertEqual(getUtilitiesFor(None, IDummyService),
                         [('',dummyService)])
        
    def testRegisteredMatching(self):
        us = getService(None, Utilities)
        self.assertEqual(queryUtility(None, IDummyService), None)
        self.assertEqual(queryUtility(None, IDummyService, self), self)
        us.provideUtility(IDummyService, dummyService)
        self.assertEqual(us.getRegisteredMatching(IDummyService),
                         [(IDummyService, '', dummyService)])

    def testRegisteredMatchingWithName(self):
        us = getService(None, Utilities)
        self.assertEqual(queryUtility(None, IDummyService), None)
        self.assertEqual(queryUtility(None, IDummyService, self), self)
        us.provideUtility(IDummyService, dummyService, 'a dummy service')
        self.assertEqual(us.getRegisteredMatching(IDummyService, 'dummy'),
                         [(IDummyService, 'a dummy service', dummyService)])
        self.assertEqual(us.getRegisteredMatching(IDummyService, 'stupid'),
                         [])

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
