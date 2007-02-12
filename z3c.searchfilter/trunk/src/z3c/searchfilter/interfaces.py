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
"""Search Criteria Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.i18nmessageid
import zope.interface
import zope.schema
from hurry import query
from zope.schema import vocabulary

_ = zope.i18nmessageid.MessageFactory('z3c.searchfilter')


class ISearchCriteria(zope.interface.Interface):
    """Search criteria for position search."""

    connector = zope.schema.Choice(
        title=_('Connector'),
        description=_('Criterium Connector'),
        vocabulary=vocabulary.SimpleVocabulary((
            vocabulary.SimpleTerm(query.Or, 'or',
                                  _('Match any of the following')),
            vocabulary.SimpleTerm(query.And, 'and',
                                  _('Match all of the following'))
            )),
        default=query.Or,
        required=True)

    def clear():
        """Clear the criteria."""

    def add(criterium):
        """Add a criterium."""

    def available():
        """Return a sequence of names of all available criteria."""

    def getAllQuery(self):
        """Get a query that returns all possible values."""

    def generateQuery():
        """Generate a query object."""


class ISearchCriterium(zope.interface.Interface):
    """A search citerium of a piece of data."""

    label = zope.schema.TextLine(
        title=_('Label'),
        description=_('Label used to present the criterium.'),
        required=True)

    def generateQuery():
        """Generate a query object."""


class IFullTextCriterium(ISearchCriterium):

    value = zope.schema.TextLine(
        title=_('Search Query'),
        required=True)


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
