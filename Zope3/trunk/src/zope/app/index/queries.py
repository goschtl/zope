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
"""Generic queries for indexes.

$Id: queries.py,v 1.2 2002/12/25 14:12:54 jim Exp $
"""

from zope.component import getAdapter
from zope.app.interfaces.index.interfaces import IBatchedResult, IRankedHubIdList

class BatchedRankedResult:

    __implements__ = IBatchedResult, IRankedHubIdList

    def __init__(self, hubidlist, startposition, batchsize, totalsize):
        self.__hubidlist = hubidlist
        self.startPosition = startposition
        self.batchSize = batchsize
        self.totalSize = totalsize

    def __getitem__(self, index):
        return self.__hubidlist[index]
