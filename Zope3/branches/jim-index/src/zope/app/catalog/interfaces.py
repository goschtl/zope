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

    def updateObject(obj):
        """Reindex the object in all indexes."""


class ICatalog(ICatalogQuery, ICatalogEdit): 
    """Marker to describe a catalog in content space."""

