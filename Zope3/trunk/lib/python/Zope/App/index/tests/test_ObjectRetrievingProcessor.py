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
##############################################################################
"""

$Id: test_ObjectRetrievingProcessor.py,v 1.1 2002/12/04 16:10:57 ctheune Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.ComponentArchitecture import getAdapter
from Zope.ComponentArchitecture import getServiceManager
from Zope.ComponentArchitecture.Exceptions import ComponentLookupError

from Interface.Verify import verifyObject
from Zope.App.tests.PlacelessSetup import PlacelessSetup

from Zope.App.OFS.Services.QueryService.IQueryProcessor import \
    IQueryProcessor
from Zope.App.OFS.Services.ObjectHub.IObjectHub import IObjectHub
    
from Zope.App.index.interfaces import IRankedHubIdList, \
    IRankedObjectIterator, IRankedObjectRecord
from Zope.App.index.processors import ObjectRetrievingProcessor
from Zope.App.index.processors import RankedObjectRecord, RankedObjectIterator
from Zope.App.index.queries import BatchedRankedResult

class FakeObjectHub:

    # This fake hub doesn't implement everything, but enough
    # to satisfy our tests

    __implements__ = IObjectHub

    def __init__(self):
        self.data = {}
        self.serial = 0

    def register(self, object):
        self.serial = self.serial + 1
        self.data[self.serial] = object
        return self.serial

    def getObject(self, id):
        return self.data[id]

#############################################################################
# If your tests change any global registries, then uncomment the
# following import and include CleanUp as a base class of your
# test. It provides a setUp and tearDown that clear global data that
# has registered with the test cleanup framework.  Don't use this
# tests outside the Zope package.

# from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

#############################################################################

class Test(PlacelessSetup, TestCase):

    ############################################################
    # Interface-driven tests:

    def test_IVerify(self):
        verifyObject(IRankedObjectRecord, RankedObjectRecord(None, None))
        verifyObject(IRankedObjectIterator, RankedObjectIterator([], None, 0, 20, 4))
        verifyObject(IQueryProcessor, ObjectRetrievingProcessor())

    def test_RankedObjectRecord(self):
        record = RankedObjectRecord(1,0.1)
        self.assertEqual(record.object, 1)
        self.assertEqual(record.rank, 0.1)

    def test_parameter(self):
        objects = [ [], [], [], [] ]
        ranked_result_set = []

        # Register the objecthub as a service
        hub = FakeObjectHub()
        service_manager = getServiceManager(None)
        service_manager.defineService("ObjectHub", IObjectHub)
        service_manager.provideService("ObjectHub", hub)

        # Insert our objects into the hub and remember their ids
        for x in objects:
            ranked_result_set.append((hub.register(x), 12))

        ranked_result_set = BatchedRankedResult(ranked_result_set, 0, 20, 4)

        processor = ObjectRetrievingProcessor()
        retrieved_result = processor(ranked_result_set)

        for x,y in zip(objects, retrieved_result):
            verifyObject(IRankedObjectRecord, y)
            self.assertEqual(id(x),id(y.object))

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
