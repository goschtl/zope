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
$Id: addservicemanager.py,v 1.3 2003/03/23 22:35:36 jim Exp $
"""

from zope.publisher.browser import BrowserView
from zope.app.services.service import ServiceManager


class AddServiceManager(BrowserView):

    def addServiceManager(self):
        sm = ServiceManager()
        if self.context.hasServiceManager():
            raise ValueError(
                  'This folder already contains a service manager')
        self.context.setServiceManager(sm)
        self.request.response.redirect("++etc++site/")
