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
from persistent import Persistent
from zope.interface import implements
from zope.app.zapi import getUtility
from zope.security.proxy import removeSecurityProxy
from zope.app.container.btree import BTreeContainer

from zope.app import zapi
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.container.interfaces import IContainer
from zope.app.catalog.interfaces import ICatalog
from zope.app.uniqueid.interfaces import IUniqueIdUtility
from zope.app.utility.interfaces import ILocalUtility
from zope.index.interfaces import ISimpleQuery


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

    implements(ICatalog, IContainer, IAttributeAnnotatable, ILocalUtility)

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
        uidutil = zapi.getUtility(IUniqueIdUtility)
        for uid, ref in uidutil.items():
            obj = ref()
            index.index_doc(uid, obj)

    def updateIndexes(self):
        uidutil = zapi.getUtility(IUniqueIdUtility)
        for uid, ref in uidutil.items():
            obj = ref()
            for index in self.values():
                index.index_doc(uid, obj)

    def searchResults(self, **searchterms):
        from BTrees.IIBTree import intersection
        pendingResults = None
        for key, value in searchterms.items():
            index = self.get(key)
            if not index:
                raise ValueError, "no such index %s" % (key, )
            index = ISimpleQuery(index)
            results = index.query(value)
            # Hm. As a result of calling getAdapter, I get back
            # security proxy wrapped results from anything that
            # needed to be adapted.
            results = removeSecurityProxy(results)
            if pendingResults is None:
                pendingResults = results
            else:
                pendingResults = intersection(pendingResults, results)
            if not pendingResults:
                break # nothing left, short-circuit
        # Next we turn the IISet of docids into a generator of objects
        uidutil = zapi.getUtility(IUniqueIdUtility)
        results = ResultSet(pendingResults, uidutil)
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
    """A subscriber to UniqueIdAddedEvent"""
    for cat in zapi.getAllUtilitiesRegisteredFor(ICatalog):
        ob = event.original_event.object
        id = zapi.getUtility(IUniqueIdUtility, context=cat).getId(ob)
        cat.index_doc(id, ob)


def reindexDocSubscriber(event):
    """A subscriber to ObjectModifiedEvent"""
    for cat in zapi.getAllUtilitiesRegisteredFor(ICatalog):
        ob = event.object
        id = zapi.getUtility(IUniqueIdUtility, context=cat).queryId(ob)
        if id is not None:
            cat.index_doc(id, ob)


def unindexDocSubscriber(event):
    """A subscriber to UniqueIdRemovedEvent"""
    for cat in zapi.getAllUtilitiesRegisteredFor(ICatalog):
        ob = event.original_event.object
        id = zapi.getUtility(IUniqueIdUtility, context=cat).queryId(ob)
        if id is not None:
            cat.unindex_doc(id)
