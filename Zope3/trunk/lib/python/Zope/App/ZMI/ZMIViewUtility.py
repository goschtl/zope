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

$Id: ZMIViewUtility.py,v 1.3 2002/06/18 19:34:57 jim Exp $
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
        browser_menu_service = getService(context, 'BrowserMenu')
        return browser_menu_service.getMenu('zmi_views',
                                            self.context,
                                            self.request)
    
