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

$Id: test_utilityservice.py,v 1.5 2003/05/01 19:35:39 faassen Exp $
"""

from unittest import TestCase, main, makeSuite
from zope.component import \
     getUtility, getService, queryUtility, getServiceManager
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Utilities
from zope.interface import Interface

from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class IDummyService(Interface):
    pass

class DummyService:
    __implements__ = IDummyService

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


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
