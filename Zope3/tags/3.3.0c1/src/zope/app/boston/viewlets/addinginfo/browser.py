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

$Id$
"""

from zope.interface import implements

from zope.app.container.interfaces import IAdding
from zope.app.zapi import queryMultiAdapter

from zope.app.i18n import ZopeMessageFactory as _
from zope.app.boston import OrderedViewlet
from zope.app.boston.viewlets.addinginfo.interfaces import IAddingInfoViewlet



class AddingInfoViewlet(OrderedViewlet):
    """I18n info viewlet."""

    implements(IAddingInfoViewlet)

    def getTitle(self):
        """Get title of viewlet"""
        return _("Adding info")

    def addingInfo(self):
        """Get adding info from IAdding view."""
        addingView = queryMultiAdapter((self.context, self.request), name='+')
        if addingView is not None:
            return addingView.addingInfo()
        else:
            return {}

    def nameAllowed(self):
        """Return whether names can be input by the user."""
        addingView = queryMultiAdapter((self.context, self.request), name='+')
        if addingView is not None:
            return addingView.nameAllowed()
        else:
            return False
