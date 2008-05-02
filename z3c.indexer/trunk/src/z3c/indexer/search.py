##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id:$
"""
__docformat__ = "reStructuredText"

import BTrees
import zope.interface
import zope.component
from zope.app.intid.interfaces import IIntIds

from z3c.indexer import interfaces


class ResultSet:
    """Lazily accessed set of objects."""

    def __init__(self, uids, intids):
        self.uids = uids
        self.intids = intids

    def __len__(self):
        return len(self.uids)

    def __contains__(self, item):
        idx = self.intids.queryId(item)
        if idx and idx in self.uids:
            return True
        else:
            return False

    def __getitem__(self, slice):
        start = slice.start
        stop = slice.stop
        if stop > len(self):
            stop = len(self)
        return [self.intids.getObject(self.uids[idx])
                for idx in range(start, stop)]

    def __iter__(self):
        for uid in self.uids:
            obj = self.intids.getObject(uid)
            yield obj


class SearchQuery(object):
    """Chainable query processor."""

    zope.interface.implements(interfaces.ISearchQuery)

    family = BTrees.family32

    def __init__(self, query=None, family=None):
        """Initialize with none or existing query."""
        res= None
        if query is not None:
            res = query.apply()
        if family is not None:
            self.family = family
        if res:
            self.results = self.family.IF.Set(res)
        else:
            self.results = self.family.IF.Set()

    def apply(self):
        return self.results

    def searchResults(self):
        results = []
        if self.results is not None:
            intids = zope.component.getUtility(IIntIds)
            results = ResultSet(self.results, intids)
        return results

    def Or(self, query):
        """Enhance search results. (union)

        The result will contain intids which exist in the existing result 
        and/or in the result from te given query.
        """
        res = query.apply()
        if res:
            self.results = self.family.IF.union(self.results, res)
        return self

    def And(self, query):
        """Restrict search results. (intersection)

        The result will only contain intids which exist in the existing
        result and in the result from te given query. (union)
        """
        res = query.apply()
        if res:
            self.results = self.family.IF.intersection(self.results, res)
        return self

    def Not(self, query):
        """Exclude search results. (difference)

        The result will only contain intids which exist in the existing
        result but do not exist in the result from te given query.
        
        This is faster if the existing result is small. But note, it get 
        processed in a chain, results added after this query get added again. 
        So probably you need to call this at the end of the chain.
        """
        res = query.apply()
        if res:
            self.results = self.family.IF.difference(self.results, res)
        return self
