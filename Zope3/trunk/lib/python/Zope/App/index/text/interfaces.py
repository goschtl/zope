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

$Id: interfaces.py,v 1.3 2002/12/04 20:00:52 gvanrossum Exp $
"""

from Interface import Interface

class ISearchableText(Interface):

    """Interface that text-indexable objects should implement."""

    def getSearchableText():
        """Return a sequence of unicode strings to be indexed.

        Each unicode string in the returned sequence will be run
        through the splitter pipeline; the combined stream of words
        coming out of the pipeline will be indexed.
        """

from Zope.TextIndex.TextIndexInterfaces import IStatistics

class IUITextIndex(IStatistics):

    """Interface for creating a TextIndex from the ZMI."""

    def subscribe():
        """Subscribe to the prevailing object hub service."""

    def unsubscribe():
        """Unsubscribe from the object hub service."""

    def isSubscribed():
        """Return whether we are currently subscribed."""
