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

$Id$
"""
from unittest import TestCase, main, makeSuite
from zope.component import \
     getUtility, getUtilitiesFor, getService, queryUtility, \
     getServiceManager, getUtilitiesFor
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Utilities
from zope.interface import Interface, implements

from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class IDummyUtility(Interface):
    pass

class DummyUtility:
    __name__ = 'DummyUtility'
    implements(IDummyUtility)

class DummyUtility2:
    implements(IDummyUtility)
    __name__ = 'DummyUtility2'

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
        from zope.component.utility import GlobalUtilityService
        provideService('Utilities', GlobalUtilityService())

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
        self.assertEqual(list(getUtilitiesFor(None, IDummyUtility)),
                         [('',dummyUtility)])
        self.assertEqual(list(us.getUtilitiesFor(IDummyUtility)),
                         [('',dummyUtility)])

    def testregistrations(self):
        us = getService(None, Utilities)
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(
            map(str, us.registrations()),
            ["UtilityRegistration('IDummyUtility', '', 'DummyUtility', '')"])


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
