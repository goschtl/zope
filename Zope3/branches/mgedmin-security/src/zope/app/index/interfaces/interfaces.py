##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Standard interfaces for using the query service.

The query service provides a set of interfaces for articulating queries. You
can create complex queries by implementing multiple interfaces like
IBatchedQuery and ITextIndexQuery to ask the TextIndex for a batched query.
The lookup for the query processor will try to find an appropriate adapter to
the index.

$Id: interfaces.py,v 1.1 2004/03/02 14:40:10 philikon Exp $
"""

from zope.interface import Interface, Attribute

class IQueryDescription(Interface):
    """An interface the describes the input or output of a
       query processor.

       There should exist an adapter that adapts the type we
       are describing to an object that implements this interface.
    """

class ITextIndexQuery(IQueryDescription):
    """A unicode query string that's compatible to the TextIndex
       syntax.
    """

    textIndexQuery = Attribute("The query.")

class IBatchedQuery(Interface):

    startPosition = Attribute("The first element of the batch.")
    batchSize = Attribute("The size of the batch.")

class IBatchedTextIndexQuery(IBatchedQuery, ITextIndexQuery):
    pass

class IBatchedResult(IBatchedQuery):

    totalSize = Attribute("The total size of the result set if known.")

class IHubIdSet(IQueryDescription):
    """Contains an IISet or IOSet of HubIds.
    """

    iset = Attribute("The set of HubIds.")

class IRankedHubIdList(IQueryDescription):
    """Describes a sequence of tuples (hubid, rank) where
       rank is a float between 0 and 1 inclusive.
    """

    def __getitem__(index):
        """Returns a tuple (hubid, rank) with that index."""

class IInstrumentalQuery(Interface):
    """The original query in a form that was actually used.
    """

    instrumentalQuery = Attribute("Contains the instrumental query.")


class IRankedObjectIterator(Interface):
    """Provides an iterable presentation of ranked results
       of a ranked query. Each item is implementing an IRankedObjectRecord.
    """

    def __iter__():
        """Iterates over the results."""

class IRankedObjectRecord(Interface):
    """One item returned by the iterator."""

    rank = Attribute("A float between 0 and 1 inclusive.")
    object = Attribute("The object.")
