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

$Id: processors.py,v 1.6 2003/05/01 19:35:20 faassen Exp $
"""

from zope.component import getAdapter

from zope.textindex.textindexinterfaces import IQuerying
from zope.app.interfaces.index.interfaces import IBatchedResult
from zope.app.interfaces.index.interfaces import IRankedHubIdList
from zope.app.interfaces.index.interfaces import IBatchedTextIndexQuery
from zope.app.interfaces.services.query import IQueryProcessor
from zope.app.index.queries import BatchedRankedResult

class BatchedRankedProcessor:

    __implements__ = IQueryProcessor
    __used_for__ = IQuerying

    inputInterfaces = (IBatchedTextIndexQuery,)
    outputInterfaces = (IRankedHubIdList, IBatchedResult)

    def __init__(self, textindex):
        self.textindex = textindex

    def __call__(self, query):
        query = getAdapter(query, IBatchedTextIndexQuery)
        resultlist, totalresults = self.textindex.query(query.textIndexQuery,
                                                        query.startPosition,
                                                        query.batchSize)

        # XXX do we need some wrapping here?
        result = BatchedRankedResult(resultlist, query.startPosition,
                                     query.batchSize, totalresults)

        return result
