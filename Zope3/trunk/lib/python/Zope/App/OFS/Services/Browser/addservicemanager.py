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
"""
$Id: addservicemanager.py,v 1.1 2002/12/20 23:13:00 jim Exp $
"""

from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Services.ServiceManager.ServiceManager import ServiceManager


class AddServiceManager(BrowserView):

    def addServiceManager(self):
        sm = ServiceManager()
        if self.context.hasServiceManager():
            raise ValueError(
                  'This folder already contains a service manager')
        self.context.setServiceManager(sm)
        self.request.response.redirect("++etc++Services/")
