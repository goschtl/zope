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

$Id: ZMIViewUtility.py,v 1.4 2002/10/22 12:11:12 stevea Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.ComponentArchitecture import getService

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
    
