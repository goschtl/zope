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

$Id: processors.py,v 1.7 2003/02/11 15:59:45 sidnei Exp $
"""

from __future__ import generators

from zope.app.interfaces.index.interfaces import \
    IRankedObjectIterator, IRankedObjectRecord, \
    IRankedHubIdList, IBatchedResult
from zope.app.interfaces.services.query import IQueryProcessor

from zope.component import getAdapter, getService
from zope.component.servicenames import HubIds
from zope.proxy.context import ContextMethod

class ObjectRetrievingProcessor:
    """Converts a RankedHubIdList into an iteratable
       list of ranked objects by retrieving the objects
       from the ObjectHub.
    """

    __implements__ = IQueryProcessor

    inputInterfaces = (IRankedHubIdList, IBatchedResult)
    outputInterfaces = (IRankedObjectIterator,)

    def __call__(wrapped_self, query):
        list = getAdapter(query, IRankedHubIdList)
        batch = getAdapter(query, IBatchedResult)

        objectHub = getService(wrapped_self, HubIds)

        # XXX do we need wrapping for the objects returned by the hub?
        iterator = RankedObjectIterator(
                        list,objectHub.getObject, batch.startPosition,
                        batch.batchSize, batch.totalSize
                        )

        return iterator
    __call__ = ContextMethod(__call__)

class RankedObjectIterator:
    """Iterates over a given list of IRankedObjectRecord."""

    __implements__ = IRankedObjectIterator, IBatchedResult

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

class RankedObjectRecord:
    """Contains a reference to a ranked object."""

    __slots__ = ["rank", "object"]

    __implements__ = IRankedObjectRecord

    def __init__(self, object, rank):
        self.rank = rank
        self.object = object
