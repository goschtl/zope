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
"""XXX short summary goes here.

$Id: queries.py,v 1.2 2002/12/25 14:12:55 jim Exp $
"""

from zope.app.interfaces.index.interfaces import \
    IBatchedTextIndexQuery, IBatchedResult, IRankedHubIdList

class BatchedTextIndexQuery:

    __implements__ = IBatchedTextIndexQuery

    def __init__(self, query, startposition, batchsize):

        self.textIndexQuery = query
        self.startPosition = startposition
        self.batchSize = batchsize
