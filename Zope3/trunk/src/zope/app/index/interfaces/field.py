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
"""Interfaces related to field indexing and searching.

$Id$
"""
from zope.interface import Interface
from zope.schema import BytesLine, Choice


class IUIFieldCatalogIndex(Interface):
    """Interface for creating a FieldIndex in a catalog from the ZMI."""

    interface = Choice(
                title=u"Interface",
                description=u"Objects will be adapted to this interface",
                vocabulary="Interfaces",
                required=False)

    field_name = BytesLine(
                title=u"Field Name",
                description=u"Name of the field to index")

class IUIFieldIndex(IUIFieldCatalogIndex):
    """Interface for creating a FieldIndex from the ZMI (not in a catalog)."""

    def subscribe():
        """Subscribe to the prevailing object hub service."""

    def unsubscribe():
        """Unsubscribe from the object hub service."""

    def isSubscribed():
        """Return whether we are currently subscribed."""

    def documentCount():
        """Return number of indexed documents """

    def search(values):
        """Return a set of hub IDs for all documents matching the values.

        'values' can be a single value or a sequence of values.  In the latter
        case the IDs of documents matching any of the values will be returned.
        """
