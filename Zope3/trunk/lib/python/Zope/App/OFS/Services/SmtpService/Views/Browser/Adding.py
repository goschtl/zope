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

class Adding(BrowserView):
    """Adding component for service containers"""

    menu_id = "add_smtp"
    __used_for__ = IAdding
    
    def action(self):
        request = self.request
        smtphost = request.get('smtphost')
        smtpport = request.get('smtpport')
        sh = SmtpService(smtphost, smtpport)
        self.context.add(sh)
        self.request.response.redirect(self.context.nextURL())
        
