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
$Id: Adding.py,
"""
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.OFS.Services.SmtpService.SmtpService \
     import SmtpService

from Zope.Proxy.ProxyIntrospection import removeAllProxies     

class Edit(BrowserView):
    """Editing smtp service container"""

    def action(self):
        request = self.request
        smtphost = request.get('smtphost')
        smtpport = request.get('smtpport')
        smtpservice = removeAllProxies(self.context)
        smtpservice.smtphost = smtphost
        smtpservice.smtpport = smtpport
        self.request.response.redirect('.')

    def edit(self):
        smtps = removeAllProxies(self.context)
        smtphost = smtps.smtphost
        smtpport = smtps.smtpport 
        return {
            'smtphost': smtphost,
            'smtpport': smtpport,
            }
        
