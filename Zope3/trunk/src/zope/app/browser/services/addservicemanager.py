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
"""Add Service Manager View Class

$Id: addservicemanager.py,v 1.4 2003/08/07 17:41:03 srichter Exp $
"""
from zope.app.services.service import ServiceManager

class AddServiceManager:

    def addServiceManager(self):
        sm = ServiceManager()
        if self.context.hasServiceManager():
            raise ValueError(
                  'This folder already contains a service manager')
        self.context.setServiceManager(sm)
        self.request.response.redirect("++etc++site/")
