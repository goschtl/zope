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

import persistent
import zope.interface
from zope.schema.fieldproperty import FieldProperty
from zope.container import contained

from z3c.i18n import MessageFactory as _
from z3c.indexer import query
from z3c.searcher import interfaces


class SearchCriterium(persistent.Persistent, contained.Contained):
    """Search criterium for some data.

    This search criterium is implemented as an adapter to the search
    """
    zope.interface.implements(interfaces.ISearchCriterium)

    label = None
    indexOrName = None

    # See interfaces.ISearchCriterium
    operator = query.Eq
    operatorLabel = _('equals')

    value = FieldProperty(interfaces.ISearchCriterium['value'])
    connectorName = FieldProperty(interfaces.ISearchCriterium['connectorName'])

    def search(self, searchQuery):
        """See interfaces.ISearchCriterium.

        Note, this can raise TypeError or zope.index.text.parsetree.ParseError 
        for text index or any other error raised from other indexes. We only
        catch te TypeError and ParseError in the offered FilterForm.
        """
        operatorQuery = self.operator(self.indexOrName, self.value)
        if self.connectorName == interfaces.CONNECTOR_OR:
            return searchQuery.Or(operatorQuery)
        if self.connectorName == interfaces.CONNECTOR_AND:
            return searchQuery.And(operatorQuery)
        if self.connectorName == interfaces.CONNECTOR_NOT:
            return searchQuery.Not(operatorQuery)


class SetSearchCriterium(SearchCriterium):

    operator = query.AnyOf
    operatorLabel = _('is')

    def search(self, searchQuery):
        """See interfaces.ISearchCriterium.

        Note, this can raise TypeError or zope.index.text.parsetree.ParseError 
        for text index or any other error raised from other indexes. We only
        catch te TypeError and ParseError in the offered FilterForm.
        """
        operatorQuery = self.operator(self.indexOrName, [self.value])
        if self.connectorName == interfaces.CONNECTOR_OR:
            return searchQuery.Or(operatorQuery)
        if self.connectorName == interfaces.CONNECTOR_AND:
            return searchQuery.And(operatorQuery)
        if self.connectorName == interfaces.CONNECTOR_NOT:
            return searchQuery.Not(operatorQuery)


class TextCriterium(SearchCriterium):
    """Search criterium for some data."""
    zope.interface.implements(interfaces.ITextCriterium)

    label = _('Text')
    operator = query.TextQuery
    operatorLabel = _('matches')
    value = FieldProperty(interfaces.ITextCriterium['value'])


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
    return type('%sFactory' %klass.__name__, (SearchCriteriumFactoryBase,),
                {'klass': klass, 'title': title})
