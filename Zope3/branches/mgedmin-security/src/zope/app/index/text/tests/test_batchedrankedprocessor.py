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

$Id: test_batchedrankedprocessor.py,v 1.12 2004/03/13 20:24:11 srichter Exp $
"""
from unittest import TestCase, main, makeSuite
from zope.app.tests.placelesssetup import PlacelessSetup

from zope.interface.verify import verifyObject
from zope.interface import implements

from zope.index.interfaces import IQuerying
from zope.app.index.interfaces.interfaces import \
    IBatchedResult, IRankedHubIdList
from zope.app.index.interfaces import IQueryProcessor
from zope.app.index.text.processors import BatchedRankedProcessor
from zope.app.index.text.queries import BatchedTextIndexQuery

class StupidTextIndex:

    implements(IQuerying)

    def __init__(self, returnvalue):
        self.returnvalue = returnvalue

    def query(self, querytext, start, count):
        """a stub query processor"""
        self.args = (querytext, start, count)

        return self.returnvalue

#############################################################################
# If your tests change any global registries, then uncomment the
# following import and include CleanUp as a base class of your
# test. It provides a setUp and tearDown that clear global data that
# has registered with the test cleanup framework.  Don't use this
# tests outside the Zope package.

# from zope.testing.cleanup import CleanUp # Base class w registry cleanup

#############################################################################

class Test(PlacelessSetup, TestCase):

    def _Test__new(self):
        return BatchedRankedProcessor()

    ############################################################
    # Interface-driven tests:

    def test_IVerify(self):
        processor = BatchedRankedProcessor(StupidTextIndex(None))
        verifyObject(IQueryProcessor, processor)

    def test_parameter(self):
        query = BatchedTextIndexQuery(u"test AND foo OR bar", 0, 20)
        index = StupidTextIndex(([], 0))

        processor = BatchedRankedProcessor(index)
        result = processor(query)

        # Do introspection for parameterpassing on the index
        self.failUnlessEqual(index.args, (u"test AND foo OR bar", 0, 20))

        # Do introspection on the result

        # BatchedResult
        batch = IBatchedResult(result)
        self.failUnlessEqual(0, batch.totalSize)
        self.failUnlessEqual(0, batch.startPosition)
        self.failUnlessEqual(20, batch.batchSize)

        # RankedHubIdList
        list = IRankedHubIdList(result)
        self.failUnlessRaises(IndexError, list.__getitem__, 0)

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
