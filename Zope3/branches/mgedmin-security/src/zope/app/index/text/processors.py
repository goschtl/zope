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
"""A query processor to the TextIndex that supports batching and ranking.

$Id: processors.py,v 1.12 2004/03/13 20:24:11 srichter Exp $
"""

from zope.index.interfaces import IQuerying
from zope.app.index.interfaces.interfaces import IBatchedResult
from zope.app.index.interfaces.interfaces import IRankedHubIdList
from zope.app.index.interfaces.interfaces import IBatchedTextIndexQuery
from zope.app.index.interfaces import IQueryProcessor
from zope.app.index.queries import BatchedRankedResult
from zope.interface import implements

class BatchedRankedProcessor:

    implements(IQueryProcessor)
    __used_for__ = IQuerying

    inputInterfaces = (IBatchedTextIndexQuery,)
    outputInterfaces = (IRankedHubIdList, IBatchedResult)

    def __init__(self, textindex):
        self.textindex = textindex

    def __call__(self, query):
        query = IBatchedTextIndexQuery(query)
        resultlist, totalresults = self.textindex.query(query.textIndexQuery,
                                                        query.startPosition,
                                                        query.batchSize)

        # XXX do we need some wrapping here?
        result = BatchedRankedResult(resultlist, query.startPosition,
                                     query.batchSize, totalresults)

        return result
