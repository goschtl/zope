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
"""Connection Management GUI

$Id: EditUser.py,v 1.2 2002/07/13 18:26:26 srichter Exp $
"""
from Zope.ComponentArchitecture import getService
from Zope.Publisher.Browser.BrowserView import BrowserView

class EditUser(BrowserView):
    
    def action(self, title, description, login, password, roles):
        user = self.context
        user.setTitle(title)
        user.setDescription(description)
        user.setLogin(login)
        if password != "DEFAULT":
            user.setPassword(password)
        user.setRoles(roles)
        return self.request.response.redirect(self.request.URL[-1])

    def getAvailableRoles(self):
        service = getService(self.context, "RoleService")
        return service.getRoles()
