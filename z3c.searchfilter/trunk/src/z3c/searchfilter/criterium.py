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
"""Search Criteria Implementation

$Id$
"""
__docformat__ = "reStructuredText"
import hurry.query.value
import hurry.query.set
import persistent
import persistent.list
import zope.component
import zope.interface
from BTrees.IFBTree import IFBTree
from hurry import query
from zope.location import location
from zope.schema.fieldproperty import FieldProperty

from z3c.searchfilter import interfaces
from z3c.searchfilter.interfaces import _

class SearchCriteria(location.Location, persistent.list.PersistentList):
    """Simple search criteria implementation.

    This component uses the component architecture to determine its available
    criterium components.
    """
    zope.interface.implements(interfaces.ISearchCriteria)

    connector = FieldProperty(interfaces.ISearchCriteria['connector'])
    # Must be implemented by sub-class or instance
    allIndex = None

    def clear(self):
        """See interfaces.ISearchCriteria"""
        super(SearchCriteria, self).__init__()
        self.connector = query.Or

    def add(self, name):
        """See interfaces.ISearchCriteria"""
        criterium = zope.component.getAdapter(
            self, interfaces.ISearchCriteriumFactory, name=name)()
        location.locate(criterium, self)
        self.append(criterium)

    def available(self):
        """See interfaces.ISearchCriteria"""
        adapters = zope.component.getAdapters(
            (self,), interfaces.ISearchCriteriumFactory)
        return sorted(adapters, key=lambda (n, a): a.weight)

    def getAllQuery(self):
        """See interfaces.ISearchCriteria"""
        return hurry.query.value.ExtentAny(self.allIndex, None)

    def generateQuery(self):
        """See interfaces.ISearchCriteria"""
        # If no criteria are selected, return all values
        if not len(self):
            return self.getAllQuery()
        # Set up the queries of the contained criteria; if one setup fails,
        # just ignore the criterium.
        queries = []
        for criterium in self:
            try:
                queries.append(criterium.generateQuery())
            except AssertionError:
                # The criterium is probably setup incorrectly
                pass
        # Match the specified criteria in comparison to all possible values.
        return query.And(self.connector(*queries), self.getAllQuery())


class SimpleSearchCriterium(persistent.Persistent):
    """Search criterium for some data.

    This search criterium is implemented as an adapter to the search
    """
    zope.interface.implements(interfaces.ISearchCriterium)

    # See interfaces.ISearchCriterium
    label = None
    value = None
    operator = query.value.Eq
    operatorLabel = _('equals')
    _index = None

    def generateQuery(self):
        """See interfaces.ISearchCriterium"""
        return self.operator(self._index, self.value)


class SimpleSetSearchCriterium(SimpleSearchCriterium):

    operator = query.set.AnyOf
    operatorLabel = _('is')

    def generateQuery(self):
        """See interfaces.ISearchCriterium"""
        return self.operator(self._index, [self.value])


class MatchFullText(query.Text):

    def apply(self):
        if not self.text:
            return IFBTree()
        return super(MatchFullText, self).apply()


class FullTextCriterium(SimpleSearchCriterium):
    """Search criterium for some data."""
    zope.interface.implements(interfaces.IFullTextCriterium)

    label = _('Text')
    operator = MatchFullText
    operatorLabel = _('matches')
    value = FieldProperty(interfaces.IFullTextCriterium['value'])


class SearchCriteriumFactoryBase(object):
    """Search Criterium Factory."""
    zope.interface.implements(interfaces.ISearchCriteriumFactory)

    klass = None
    title = None
    weight = 0

    def __init__(self, context):
        pass

    def __call__(self):
        return self.klass()

def factory(klass, title):
    return type('%sFactory' %klass.__name__, (SearchCriteriumFactory,),
                {'klass': klass, 'title': title})
