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
"""Interfaces for a text index.

$Id: textindexinterfaces.py,v 1.2 2002/12/25 14:15:34 jim Exp $
"""

from zope.interface import Interface


class IInjection(Interface):
    """Interface for injecting documents into an index."""

    def index_doc(docid, texts):
        """Add a document to the index.

        docid: int, identifying the document
        texts: list of unicode, the text to be indexed in a list
        return: None

        This can also be used to reindex documents.
        """

    def unindex_doc(docid):
        """Remove a document from the index.

        docid: int, identifying the document
        return: None

        If docid does not exist, KeyError is raised.
        """

class IQuerying(Interface):

    def query(querytext, start=0, count=None):
        """Execute a query.

        querytext: unicode, the query expression
        start: the first result to return (0-based)
        count: the maximum number of results to return (default: all)
        return: ([(docid, rank), ...], total)

        The return value is a triple:
            matches: list of (int, float) tuples, docid and rank
            total: int, the total number of matches

        The matches list represents the requested batch.  The ranks
        are floats between 0 and 1 (inclusive).
        """

class IStatistics(Interface):

    def documentCount():
        """Return the number of documents currently indexed."""

    def wordCount():
        """Return the number of words currently indexed."""
