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

$Id: field.py,v 1.1 2003/03/26 16:10:09 andreasjung Exp $
"""

from zope.interface import Interface


class IUIFieldIndex(Interface):

    """Interface for creating a FieldIndex from the ZMI."""

    def subscribe():
        """Subscribe to the prevailing object hub service."""

    def unsubscribe():
        """Unsubscribe from the object hub service."""

    def isSubscribed():
        """Return whether we are currently subscribed."""

    def documentCount():
        """Return number of indexed documents """

