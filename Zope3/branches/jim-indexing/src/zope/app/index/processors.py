##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Generic query processors for use with multiple indexes..

$Id$
"""
from zope.app.index.interfaces.interfaces import \
    IRankedObjectIterator, IRankedObjectRecord, \
    IRankedHubIdList, IBatchedResult
from zope.app.index.interfaces import IQueryProcessor

from zope.component import getService
from zope.app.servicenames import HubIds
from zope.app.container.contained import Contained
from zope.interface import implements

class ObjectRetrievingProcessor(Contained):
    """Converts a RankedHubIdList into an iteratable
       list of ranked objects by retrieving the objects
       from the ObjectHub.
    """

    implements(IQueryProcessor)

    inputInterfaces = (IRankedHubIdList, IBatchedResult)
    outputInterfaces = (IRankedObjectIterator,)

    def __call__(self, query):
        list = IRankedHubIdList(query)
        batch = IBatchedResult(query)

        objectHub = getService(HubIds)

        # XXX do we need wrapping for the objects returned by the hub?
        iterator = RankedObjectIterator(
                        list,objectHub.getObject, batch.startPosition,
                        batch.batchSize, batch.totalSize
                        )

        return iterator

class RankedObjectIterator:
    """Iterates over a given list of IRankedObjectRecord."""

    implements(IRankedObjectIterator, IBatchedResult)

    def __init__(self, recordlist, objectfetcher, startposition,
                 batchsize, totalsize):
        self._records = recordlist
        self.startPosition = startposition
        self.batchSize = batchsize
        self.totalSize = totalsize
        self.__objectfetcher = objectfetcher

    def __iter__(self):
        objectfetcher = self.__objectfetcher

        for hubid, rank in self._records:
            # XXX maybe we should catch some exceptions like security related
            # ones or NotFoundError, to avoid breaking the iteration. Think
            # about yielding an NotFound-Indicator in such a case.
            yield RankedObjectRecord(objectfetcher(hubid), rank)
        raise StopIteration

class RankedObjectRecord(object):
    """Contains a reference to a ranked object."""

    __slots__ = ["rank", "object"]

    implements(IRankedObjectRecord)

    def __init__(self, object, rank):
        self.rank = rank
        self.object = object
