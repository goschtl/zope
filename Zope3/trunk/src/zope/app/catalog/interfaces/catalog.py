##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Catalog Interfaces

$Id$
"""
from zope.interface import Interface

class ICatalogView(Interface):
    """Provides information about a catalog."""

    def getSubscribed():
        """Return 'True', if the catalog is subscribed to events, otherwise
        'False'."""


class ICatalogQuery(Interface):
    "Provides Catalog Queries"

    def searchResults(**kw):
        "search on the given indexes"


class ICatalogEdit(Interface):
    """Allows one to manipulate the Catalog information."""

    def clearIndexes(): 
        """Remove all index data."""

    def updateIndexes(): 
        """Reindex all objects."""

    def subscribeEvents(update=True): 
        """Start listening for events.

        Starts listening to events for possible index updating. If 'update' is
        'True', always reindex all objects.
        """

    def unsubscribeEvents(): 
        """Stop listening to events."""


class ICatalog(ICatalogView, ICatalogQuery, ICatalogEdit): 
    """Marker to describe a catalog in content space."""

