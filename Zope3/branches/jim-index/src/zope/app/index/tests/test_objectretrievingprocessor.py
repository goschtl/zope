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
$Id$
"""
from unittest import TestCase, main, makeSuite
from zope.interface import implements
from zope.interface.verify import verifyObject

from zope.component import getGlobalServices
from zope.app.servicenames import HubIds

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.index.interfaces import IQueryProcessor
from zope.app.hub.interfaces import IObjectHub

from zope.app.index.interfaces.interfaces import \
     IRankedObjectIterator, IRankedObjectRecord
from zope.app.site.interfaces import ISimpleService
from zope.app.index.processors import ObjectRetrievingProcessor
from zope.app.index.processors import RankedObjectRecord, RankedObjectIterator
from zope.app.index.queries import BatchedRankedResult

class FakeObjectHub:

    # This fake hub doesn't implement everything, but enough
    # to satisfy our tests

    implements(IObjectHub, ISimpleService)

    def __init__(self):
        self.data = {}
        self.serial = 0

    def register(self, object):
        self.serial = self.serial + 1
        self.data[self.serial] = object
        return self.serial

    def getObject(self, id):
        return self.data[id]


class Test(PlacelessSetup, TestCase):

    # Interface-driven tests

    def test_IVerify(self):
        verifyObject(IRankedObjectRecord, RankedObjectRecord(None, None))
        verifyObject(IRankedObjectIterator,
                     RankedObjectIterator([], None, 0, 20, 4))
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
        service_manager = getGlobalServices()
        service_manager.defineService(HubIds, IObjectHub)
        service_manager.provideService(HubIds, hub)

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
