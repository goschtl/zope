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

$Id: processors.py,v 1.1 2002/12/04 11:55:15 ctheune Exp $
"""

from Zope.ComponentArchitecture import getAdapter

from Zope.TextIndex.TextIndexInterfaces import IQuerying
from Zope.App.index.interfaces import \
    IBatchedResult, IRankedHubIdList, IBatchedTextIndexQuery
from Zope.App.OFS.Services.QueryService.IQueryProcessor import \
    IQueryProcessor
from queries import BatchedTextIndexQuery, BatchedRankedResult

class IBatchedRankedProcessor(IQueryProcessor):
    # XXX until named adapters are there
    pass

class BatchedRankedProcessor:

    __implements__ = IBatchedRankedProcessor
    __used_for__ = IQuerying

    input_interface = IBatchedTextIndexQuery
    output_interface = (IRankedHubIdList, IBatchedResult)

    def __init__(self, textindex):
        self.__textindex = textindex

    def __call__(self, query):
        query = getAdapter(query, IBatchedTextIndexQuery)
        resultlist, totalresults = self.__textindex.query(query.textIndexQuery, \
                    query.startPosition, query.batchSize)
                    
        # XXX do we need some wrapping here?
        result = BatchedRankedResult(resultlist, query.startPosition, \
                    query.batchSize, totalresults)
                    
        return result
