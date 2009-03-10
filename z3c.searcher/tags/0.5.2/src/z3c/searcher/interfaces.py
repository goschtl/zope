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

import zope.i18nmessageid
import zope.interface
import zope.schema
from zope.schema import vocabulary
from zope.session.interfaces import ISession
from zope.location.interfaces import ILocation

from z3c.indexer import interfaces
from z3c.indexer import query
from z3c.form.interfaces import IForm
from z3c.table.interfaces import ITable

_ = zope.i18nmessageid.MessageFactory('z3c')


SEARCH_SESSION = u'z3c.search.intefaces.ISearchSession'
SEARCH_SESSION_FILTER_KEY = 'default'

CONNECTOR_OR = 'OR'
CONNECTOR_AND = 'AND'
CONNECTOR_NOT = 'NOT'

NOVALUE = object()


class ISearchSession(ISession):
    """Search session supporting API for filter management.

    Filters contain the criterium rows and are stored persistent

    The methods support a key argument. This could be a context reference key
    give from the IntId utility or some other discriminator.  If we do not 
    support a key, the string ``default`` is used.
    """

    def getFilter(name, key=SEARCH_SESSION_FILTER_KEY):
        """Return search filter by name."""

    def getFilters(name):
        """Return a list of search filters."""

    def addFilter(name, searchFilter, key=SEARCH_SESSION_FILTER_KEY):
        """Add search filter."""

    def removeFilter(name, key=SEARCH_SESSION_FILTER_KEY):
        """Remove search filter."""


connectorVocabulary = vocabulary.SimpleVocabulary([
    vocabulary.SimpleTerm(CONNECTOR_OR, title=_('or')),
    vocabulary.SimpleTerm(CONNECTOR_AND, title=_('and')),
    vocabulary.SimpleTerm(CONNECTOR_NOT, title=_('not')),
    ])

class ISearchCriterium(ILocation):
    """A search citerium of a piece of data."""

    __name__ = zope.schema.TextLine(
        title=_('Name'),
        description=_('The locatable criterium name.'),
        required=True)

    label = zope.schema.TextLine(
        title=_('Label'),
        description=_('Label used to present the criterium.'),
        required=True)

    operatorLabel = zope.schema.TextLine(
        title=_('Operator label'),
        description=_('The operator label.'),
        required=True)

    indexOrName = zope.interface.Attribute("Index or index name.")

    operator = zope.schema.Object(
        title=_('Operator'),
        description=_('The operator used for the chain the queries.'),
        schema=interfaces.IQuery,
        required=True)

    connectorName = zope.schema.Choice(
        title=_('Connector Name'),
        description=_('The criterium connector name.'),
        vocabulary=connectorVocabulary,
        default=CONNECTOR_OR,
        required=True)

    value = zope.schema.TextLine(
        title=_('Search Query'),
        required=True)

    def search(searchQuery):
        """Generate chainable search query."""


class ITextCriterium(ISearchCriterium):
    """Sample full text search criterium implementation."""


class ISearchCriteriumFactory(zope.interface.Interface):
    """A factory for the search criterium"""

    title = zope.schema.TextLine(
        title=_('Title'),
        description=_('A human-readable title of the criterium.'),
        required=True)

    weight = zope.schema.Int(
        title=_('Int'),
        description=_('The weight/importance of the factory among all '
                      'factories.'),
        required=True)

    def __call__():
        """Generate the criterium."""


class ISearchFilter(zope.interface.Interface):
    """Search criteria for position search."""

    criteria = zope.interface.Attribute(
        """Return a sequence of selected criteria.""")

    criteriumFactories = zope.schema.List(
        title=_('Criteria factories'),
        description=_('The criteria factories.'),
        value_type=zope.schema.Object(
            title=_('Criterium factory'),
            description=_('The criterium factory.'),
            schema=ISearchCriteriumFactory,
            required=True),
        default=[])

    def clear():
        """Clear the criteria."""

    def createCriterium(name, value=NOVALUE):
        """Create a criterium by factory name."""

    def addCriterium(criterium):
        """Add a criterium by name at the end of the list."""

    def createAndAddCriterium(name, value=NOVALUE):
        """Create and add a criterium by name at the end of the list."""

    def removeCriterium(criterium):
        """Add a criterium by name at the end of the list."""

    def getDefaultQuery():
        """Get a query that returns the default values. 
        
        Override this method in your custom search filter if needed.
        This query get used if ``NO`` criterias are available.
        """

    def getAndQuery():
        """Return a ``And`` query which get used by default or None.
        
        Override this method in your custom search filter if needed.
        This query get used if ``one or more`` criterias are available.
        """

    def getNotQuery():
        """Return a ``Not`` query which get used as starting query or None.
        
        Override this method in your custom search filter if needed.
        This query get used if ``one or more`` criterias are available.
        """

    def generateQuery():
        """Generate a query object."""


class IFilterForm(IForm):
    """Filter form."""


class ISearchForm(IForm):
    """Search form."""


class ISearchTable(ITable):
    """Search table."""
