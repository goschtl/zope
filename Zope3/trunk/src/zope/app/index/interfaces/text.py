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
"""Interfaces related to text indexing and searching.

$Id$
"""
from zope.interface import Interface
from zope.schema import BytesLine, Choice
from zope.index.interfaces import IStatistics


class ISearchableText(Interface):

    """Interface that text-indexable objects should implement."""

    def getSearchableText():
        """Return a sequence of unicode strings to be indexed.

        Each unicode string in the returned sequence will be run
        through the splitter pipeline; the combined stream of words
        coming out of the pipeline will be indexed.

        returning None indicates the object should not be indexed
        """

class IUITextCatalogIndex(IStatistics):
    """Interface for creating a TextIndex inside a catalog"""

    interface = Choice(
                title=u"Interface", 
                description=u"Objects will be adapted to this interface",
                vocabulary="Interfaces",
                required=False,
                default=ISearchableText)

    field_name = BytesLine(
                 title=u"Field Name",
                 description=u"Name of the field to index", 
                 default="getSearchableText")

class IUITextIndex(IUITextCatalogIndex):
    """Interface for creating a TextIndex from the ZMI."""

    def subscribe():
        """Subscribe to the prevailing object hub service."""

    def unsubscribe():
        """Unsubscribe from the object hub service."""

    def isSubscribed():
        """Return whether we are currently subscribed."""

class IQueryView(Interface):
    """Interface providing a query method that can be invoked from ZPT.

    XXX How to express that this is a browser interface?"""

    def query():
        """Perform a batched query, based on request fields.

        These request fields are used as input:

        start -- batch start (0-based); defaults to 0
        count -- batch size; defaults to 10
        queryText -- query expression; must be given

        Return a dict with fields:

        results -- a list containing the requested batch
        nresults -- number of items in results
        first -- 1-based ordinal this batch's first item
        last -- 1-based ordinal of if this batch's last item
        next -- 0-based ordinal of next batch; not set if no next batch
        prev -- 0-based ordinal of previous batch; not set if no prev batch
        count -- requested batch size
        total -- total number of matches (all batches together)

        Each item in the results set has the following string fields:

        location -- location of the object (usable as URL within the site)
        title -- Dublin Core title of the object; not present if no title
        score -- score, as a float in the range [0.0 ... 1.0]
        scoreLabel -- score, formatted as a percentage and rounded to 0.1%
        """

    def nextBatch():
        """Return the start for the next batch."""

    def prevBatch():
        """Return the start for the previous batch."""
