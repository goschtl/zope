##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Multi-field index implementation

$Id$
"""
from BTrees.IFBTree import weightedIntersection
from zope.app.container.btree import BTreeContainer
from zope.app.container.interfaces import IObjectAddedEvent
from zope.component import adapter
from zope.interface import implements

from z3c.multifieldindex.interfaces import IMultiFieldIndex
from z3c.multifieldindex.interfaces import ISubIndexFactory


class MultiFieldIndexBase(BTreeContainer):
    implements(IMultiFieldIndex)
    
    def _fields(self):
        """To be overriden. Should return an iterable of (name, field) pairs."""
        raise NotImplemented('_fields method should be provided by subclass.')
    
    def _getData(self, object):
        """To be overriden. Should return a dictionary of data for given object.
        
        Dictionary keys are the same as field/index names and values are actual
        values to be indexed by according index.
        """
        raise NotImplemented('_getData method should be provided by subclass.')
    
    def recreateIndexes(self):
        # 1. Remove all indexes
        for name in list(self.keys()):
            del self[name]
        
        # 2. Create new indexes for fields that want to be indexed
        for name, field in self._fields():
            factory = ISubIndexFactory(field)
            self[name] = factory()
    
    def index_doc(self, docid, value):
        data = self._getData(value)
        for name in self:
            value = data.get(name)
            if value is not None:
                self[name].index_doc(docid, value)
    
    def unindex_doc(self, docid):
        for index in self.values():
            index.unindex_doc(docid)
    
    def clear(self):
        for index in self.values():
            index.clear()

    def apply(self, query):
        results = []
        for name, subquery in query.items():
            if name not in self:
                continue
            r = self[name].apply(subquery)
            if r is None:
                continue
            if not r:
                return r
            results.append((len(r), r))

        if not results:
            return None

        results.sort()
        _, result = results.pop(0)
        for _, r in results:
            _, result = weightedIntersection(result, r)

        return result


@adapter(IMultiFieldIndex, IObjectAddedEvent)
def multiFieldIndexAdded(index, event):
    index.recreateIndexes()
