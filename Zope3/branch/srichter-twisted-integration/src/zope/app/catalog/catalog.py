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
"""Catalog

$Id$
"""
from zope.interface import implements
from zope.app.container.btree import BTreeContainer
import zope.index.interfaces

from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.container.interfaces import IContainer
from zope.app.catalog.interfaces import ICatalog
from zope.app.intid.interfaces import IIntIds
from BTrees.IFBTree import weightedIntersection

class ResultSet:
    """Lazily accessed set of objects."""

    def __init__(self, uids, uidutil):
        self.uids = uids
        self.uidutil = uidutil

    def __len__(self):
        return len(self.uids)

    def __iter__(self):
        for uid in self.uids:
            obj = self.uidutil.getObject(uid)
            yield obj


class Catalog(BTreeContainer):

    implements(ICatalog,
               IContainer,
               IAttributeAnnotatable,
               zope.index.interfaces.IIndexSearch,
               )

    def clear(self):
        for index in self.values():
            index.clear()

    def index_doc(self, docid, texts):
        """Register the data in indexes of this catalog."""
        for index in self.values():
            index.index_doc(docid, texts)

    def unindex_doc(self, docid):
        """Unregister the data from indexes of this catalog."""
        for index in self.values():
            index.unindex_doc(docid)

    def updateIndex(self, index):
        uidutil = zapi.getUtility(IIntIds)
        for uid in uidutil:
            obj = uidutil.getObject(uid)
            index.index_doc(uid, obj)

    def updateIndexes(self):
        uidutil = zapi.getUtility(IIntIds)
        for uid in uidutil:
            obj = uidutil.getObject(uid)
            for index in self.values():
                index.index_doc(uid, obj)

    def apply(self, query):
        results = []
        for index_name, index_query in query.items():
            index = self[index_name]
            r = index.apply(index_query)
            if r is None:
                continue
            if not r:
                # empty results
                return r
            results.append((len(r), r))

        if not results:
            # no applicable indexes, so catalog was not applicable
            return None

        results.sort() # order from smallest to largest
        
        _, result = results.pop(0)
        for _, r in results:
            _, result = weightedIntersection(result, r)
            
        return result

    def searchResults(self, **searchterms):
        results = self.apply(searchterms)
        if results is not None:
            uidutil = zapi.getUtility(IIntIds)
            results = ResultSet(results, uidutil)
        return results

def indexAdded(index, event):
    """When an index is added to a catalog, we have to index existing objects

       When an index is added, we tell it's parent to index it:

         >>> class FauxCatalog:
         ...     def updateIndex(self, index):
         ...         self.updated = index

         >>> class FauxIndex:
         ...     pass

         >>> index = FauxIndex()
         >>> index.__parent__ = FauxCatalog()

         >>> indexAdded(index, None)
         >>> index.__parent__.updated is index
         True
       """
    index.__parent__.updateIndex(index)
    
def indexDocSubscriber(event):
    """A subscriber to IntIdAddedEvent"""
    for cat in zapi.getAllUtilitiesRegisteredFor(ICatalog):
        ob = event.object
        id = zapi.getUtility(IIntIds, context=cat).getId(ob)
        cat.index_doc(id, ob)


def reindexDocSubscriber(event):
    """A subscriber to ObjectModifiedEvent"""
    for cat in zapi.getAllUtilitiesRegisteredFor(ICatalog):
        ob = event.object
        id = zapi.getUtility(IIntIds, context=cat).queryId(ob)
        if id is not None:
            cat.index_doc(id, ob)


def unindexDocSubscriber(event):
    """A subscriber to IntIdRemovedEvent"""
    for cat in zapi.getAllUtilitiesRegisteredFor(ICatalog):
        ob = event.object
        id = zapi.getUtility(IIntIds, context=cat).queryId(ob)
        if id is not None:
            cat.unindex_doc(id)
