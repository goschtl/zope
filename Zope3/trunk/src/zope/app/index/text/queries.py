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

$Id: queries.py,v 1.3 2003/05/01 19:35:20 faassen Exp $
"""

from zope.app.interfaces.index.interfaces import IBatchedTextIndexQuery

class BatchedTextIndexQuery:

    __implements__ = IBatchedTextIndexQuery

    def __init__(self, query, startposition, batchsize):

        self.textIndexQuery = query
        self.startPosition = startposition
        self.batchSize = batchsize
