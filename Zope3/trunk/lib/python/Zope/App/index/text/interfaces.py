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

$Id: interfaces.py,v 1.5 2002/12/06 14:49:11 gvanrossum Exp $
"""

from Interface import Interface

class ISearchableText(Interface):

    """Interface that text-indexable objects should implement."""

    def getSearchableText():
        """Return a sequence of unicode strings to be indexed.

        Each unicode string in the returned sequence will be run
        through the splitter pipeline; the combined stream of words
        coming out of the pipeline will be indexed.

        returning None indicates the object should not be indexed
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

    # XXX The following are blatant view helpers.  Need refactoring.

    def hubid2location(hubid):
        """Return a location string given a hubid."""

    def hubid2object(hubid):
        """Return an object given a hubid."""

    def hubid2title(hubid):
        """Return the Dublin Core title of the object from the hubid.

        Return '' if there is no object or if it isn't adaptable to
        IZopeDublinCore.
        """
