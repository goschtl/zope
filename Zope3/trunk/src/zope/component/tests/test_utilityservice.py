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
"""Utility service tests

$Id: test_utilityservice.py,v 1.9 2004/01/29 17:36:50 srichter Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.component import \
     getUtility, getUtilitiesFor, getService, queryUtility, getServiceManager
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Utilities
from zope.interface import Interface, implements

from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class IDummyUtility(Interface):
    pass

class DummyUtility:
    implements(IDummyUtility)

class DummyUtility2:
    implements(IDummyUtility)

    def __len__(self):
        return 0

dummyUtility = DummyUtility()
dummyUtility2 = DummyUtility2()

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
            ComponentLookupError, getUtility, None, IDummyUtility)
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(getUtility(None, IDummyUtility), dummyUtility)

    def testQueryUtility(self):
        us = getService(None, Utilities)
        self.assertEqual(queryUtility(None, IDummyUtility), None)
        self.assertEqual(queryUtility(None, IDummyUtility, self), self)
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(queryUtility(None, IDummyUtility), dummyUtility)

    def testgetUtilitiesFor(self):
        us = getService(None, Utilities)
        us.provideUtility(IDummyUtility, dummyUtility)
        conns = getUtilitiesFor(None, IDummyUtility)
        self.assertEqual(getUtilitiesFor(None, IDummyUtility),
                         [('',dummyUtility)])
        
    def testRegisteredMatching(self):
        us = getService(None, Utilities)
        self.assertEqual(queryUtility(None, IDummyUtility), None)
        self.assertEqual(queryUtility(None, IDummyUtility, self), self)
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(us.getRegisteredMatching(IDummyUtility),
                         [(IDummyUtility, '', dummyUtility)])

    def testRegisteredMatchingWithName(self):
        us = getService(None, Utilities)
        self.assertEqual(queryUtility(None, IDummyUtility), None)
        self.assertEqual(queryUtility(None, IDummyUtility, self), self)
        us.provideUtility(IDummyUtility, dummyUtility, 'dummy')
        us.provideUtility(IDummyUtility, dummyUtility2, 'another')
        self.assertEqual(us.getRegisteredMatching(IDummyUtility, 'dummy'),
                         [(IDummyUtility, 'dummy', dummyUtility)])
        self.assertEqual(us.getRegisteredMatching(IDummyUtility, 'another'),
                         [(IDummyUtility, 'another', dummyUtility2)])
        res = us.getRegisteredMatching(IDummyUtility)
        res.sort()
        self.assertEqual(res,
                         [(IDummyUtility, 'another', dummyUtility2),
                          (IDummyUtility, 'dummy',   dummyUtility )])
        self.assertEqual(us.getRegisteredMatching(IDummyUtility, 'stupid'),
                         [])

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
