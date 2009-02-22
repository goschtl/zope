##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

import persistent
import persistent.list
import zope.component
import zope.interface
import zope.event
import zope.lifecycleevent
from zope.location import location
from zope.container import contained

from z3c.indexer import query
from z3c.indexer.search import SearchQuery
from z3c.searcher import interfaces


class EmptyTerm(object):
    """Return a empty list as result."""

    def apply(self):
        return []


class SearchFilter(persistent.Persistent, contained.Contained):
    """Persistent search filter implementation.

    This component uses the component architecture to determine its available
    criterium components.
    """
    zope.interface.implements(interfaces.ISearchFilter)

    def __init__(self):
        super(SearchFilter, self).__init__()
        self.criteria = persistent.list.PersistentList()

    def clear(self):
        """See interfaces.ISearchFilter"""
        self.__init__()

    @property
    def criteriumFactories(self):
        """See interfaces.ISearchFilter"""
        adapters = zope.component.getAdapters(
            (self,), interfaces.ISearchCriteriumFactory)
        return sorted(adapters, key=lambda (n, a): a.weight)

    def createCriterium(self, name, value=interfaces.NOVALUE):
        """Create a criterium."""
        criterium = zope.component.getAdapter(
            self, interfaces.ISearchCriteriumFactory, name=name)()
        if value is not interfaces.NOVALUE:
            criterium.value = value
        criterium.__name__ = name
        criterium.__parent__ = self
        return criterium

    def addCriterium(self, criterium):
        """See interfaces.ISearchFilter"""
        location.locate(criterium, self)
        self.criteria.append(criterium)

    def createAndAddCriterium(self, name, value=interfaces.NOVALUE):
        criterium = self.createCriterium(name)
        if value is not interfaces.NOVALUE:
            criterium.value = value
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(criterium))
        self.addCriterium(criterium)

    def removeCriterium(self, criterium):
        """See interfaces.ISearchFilter"""
        self.criteria.remove(criterium)

    def getDefaultQuery(self):
        """See interfaces.ISearchFilter"""
        return EmptyTerm()

    def getAndQuery(self):
        """See interfaces.ISearchFilter"""
        return None

    def getNotQuery(self):
        """See interfaces.ISearchFilter"""
        return None

    def generateQuery(self):
        """See interfaces.ISearchFilter"""
        # If no criteria are selected, return all values
        if not len(self.criteria):
            return self.getDefaultQuery()

        searchQuery = SearchQuery()

        # order the criterium by the order or, and, not
        orCriteria = []
        andCriteria  = []
        notCriteria  = []
        for criterium in self.criteria:
            if criterium.connectorName == interfaces.CONNECTOR_OR:
                orCriteria.append(criterium)
            if criterium.connectorName == interfaces.CONNECTOR_AND:
                andCriteria.append(criterium)
            if criterium.connectorName == interfaces.CONNECTOR_NOT:
                notCriteria.append(criterium)

        # apply given ``or`` criteria if any
        for criterium in orCriteria:
            searchQuery = criterium.search(searchQuery)

        # apply given ``and`` criteria if any
        for criterium in andCriteria:
            searchQuery = criterium.search(searchQuery)

        # apply default ``And`` query if available
        andQuery = self.getAndQuery()
        if andQuery is not None:
            searchQuery = searchQuery.And(andQuery)

        # apply (remove) default ``Not`` query if available
        notQuery = self.getNotQuery()
        if notQuery is not None:
            return query.Not(self.getNotQuery)

        # apply given ``not`` criteria if any
        for criterium in notCriteria:
            searchQuery = criterium.search(searchQuery)

        return searchQuery
