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

$Id: auth.py,v 1.3 2003/03/25 11:44:10 tseaver Exp $
"""
from zope.publisher.browser import BrowserView
from zope.app.services.auth import User
from zope.component import getService

class AddUser(BrowserView):

    def action(self, id, title, description, login, password, roles):
        user = User(id, title, description, login, password)
        self.context.setObject(id, user)
        return self.request.response.redirect(self.request.URL[-2])

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
        service = getService(self.context, "Roles")
        return service.getRoles()
