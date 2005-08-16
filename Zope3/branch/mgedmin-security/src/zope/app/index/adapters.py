##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Index-relevant adapters.

$Id: adapters.py,v 1.8 2004/02/25 23:02:26 faassen Exp $
"""
from zope.index.interfaces import IQuerying, IKeywordQuerying
from BTrees.IIBTree import IISet

class SimpleQuery:
    "Call an IQuerying search, return only the hubids"
    __used_for__ = IQuerying

    def __init__(self, index):
        self._index = index

    def query(self, term, start=0, count=None):
        reslist, count = self._index.query(term, start, count)
        # Not really optimal, this. May be a better way?
        reslist = IISet([ x[0] for x in reslist ])
        return reslist

class SimpleKeywordQuery:
    "Call an IKeywordQuerying search, return only the hubids"
    __used_for__ = IKeywordQuerying

    def __init__(self, index):
        self._index = index

    def query(self, term, start=0, count=None):
        reslist = self._index.search(term, operator='and')
        return reslist


