##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import zope.interface

class ITagger(zope.interface.Interface):
    """A utility to provide POS tag extractions from a given text."""

    def initialize():
        """Initializes the tagger.

        This method only needs to be called once. It should do any expensive
        initial computation, such as creating indices, loading the lexicon,
        etc.
        """

    def tokenize(text):
        """Tokenize the given text into single words."""

    def tag(terms):
        """Returns the tagged list of terms.

        Additionally, all terms are normalized.

        The ouput format is a list of: (term, tag, normalized-term)
        """

    def __call__(text):
        """Get a tagged list of words."""


class IKeywordExtractor(zope.interface.Interface):
    """Extract important keywords from a given text."""

    def __call__(text):
        """Returns a list of extracted keywords, the amount of occurences and
        their search strength."""
