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
"""Connection Management GUI

$Id: AddUser.py,v 1.1 2002/07/13 16:52:58 srichter Exp $
"""
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.App.OFS.Services.AuthenticationService.User import User

class AddUser(BrowserView):
    
    def action(self, id, title, description, login, password, roles):
        user = User(id, title, description, login, password)
        self.context.setObject(id, user)
        return self.request.response.redirect(self.request.URL[-2])
