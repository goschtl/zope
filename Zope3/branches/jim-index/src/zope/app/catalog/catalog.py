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
from persistent.dict import PersistentDict
from zope.interface import implements
from zope.exceptions import NotFoundError
from zope.security.proxy import trustedRemoveSecurityProxy
from zope.index.interfaces import ISimpleQuery

from zope.app.zapi import getUtility, getPath
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.utility.interfaces import ILocalUtility
from zope.app.container.interfaces import IContainer

from zope.app.container.sample import SampleContainer
from zope.app.catalog.interfaces import ICatalog
from zope.app.uniqueid.interfaces import IUniqueIdUtility

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


class CatalogBase(Persistent, SampleContainer):

    implements(ICatalog, IContainer, IAttributeAnnotatable)

    def clearIndexes(self):
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

    def updateIndexes(self):
        uidutil = getUtility(IUniqueIdUtility)
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
            results = trustedRemoveSecurityProxy(results)
            if pendingResults is None:
                pendingResults = results
            else:
                pendingResults = intersection(pendingResults, results)
            if not pendingResults:
                break # nothing left, short-circuit
        # Next we turn the IISet of docids into a generator of objects
        uidutil = getUtility(IUniqueIdUtility)
        results = ResultSet(pendingResults, uidutil)
        return results


class CatalogUtility(CatalogBase):
    """A catalog in service-space."""
    # Utilities will default to implementing the most specific
    # interface. This piece of delightfulness is needed because
    # the interface resolution order machinery implements (no
    # pun intended) the old-style Python resolution order machinery.
    implements(ILocalUtility)


class Catalog(CatalogBase):
    """A catalog in content-space."""
