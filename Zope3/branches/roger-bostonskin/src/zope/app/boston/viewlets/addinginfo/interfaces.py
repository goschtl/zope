##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Boston skin

$Id:$
"""

__docformat__ = "reStructuredText"

from zope.viewlet.interfaces import IViewlet



class IAddingInfoViewlet(IViewlet):
    """Adding info API for the adapted context."""

    def getTitle():
        """Get title of viewlet"""

    def addingInfo():
        """Get adding info from IAdding view. Return menu data.

        This is sorted by title.
        """

    def nameAllowed(self):
        """Return whether names can be input by the user."""