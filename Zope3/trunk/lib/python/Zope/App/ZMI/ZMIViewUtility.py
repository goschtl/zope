##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""

$Id: ZMIViewUtility.py,v 1.2 2002/06/10 23:28:19 jim Exp $
"""

from Zope.ComponentArchitecture.ContextDependent import ContextDependent
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getService
from Zope.App.ZopePublication.PublicationTraverse \
     import PublicationTraverser
from Zope.Exceptions import Unauthorized, Forbidden

from Interface import Interface


class IZMIViewUtility(Interface):
    def getZMIViews():
        """Get available view information

        Return a sequence of dictionaries with view labels and
        actions, where actions are relative URLs.
        """


class ZMIViewUtility(BrowserView):

    def getZMIViews(self):

        context = self.context
        request = self.request
        zmi_view_service = getService(context, 'ZMIViewService')
        zmi_views=[]
        traverser = PublicationTraverser()
        for view in zmi_view_service.getViews(context):
            label=view[0]
            action=view[1]
            if action:
                try:
                    # tickle the security proxy's checker
                    # we're assuming that view pages are callable
                    # this is a pretty sound assumption
                    traverser.traversePath(request, context, action).__call__
                except (Unauthorized, Forbidden):
                    continue # Skip unauthorized or forbidden
            zmi_views.append({'label': label, 'action': "%s" % action})

        return zmi_views
    
