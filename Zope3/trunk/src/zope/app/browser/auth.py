##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Login and Logout screens

$Id: auth.py,v 1.1 2003/08/01 03:21:28 srichter Exp $
"""
from zope.interface import implements
from zope.app.interfaces.publisher.http import ILogin, ILogout
from zope.app.security.registries.principalregistry import \
     UnauthenticatedPrincipal
from zope.app.pagetemplate import ViewPageTemplateFile

class HTTPAuthenticationLogin(object):

    implements(ILogin)

    def login(self, nextURL=None):
        """See zope.app.interfaces.security.ILogin"""
        if isinstance(self.request.user, UnauthenticatedPrincipal):
            self.request.unauthorized("basic realm='Zope'")
        else:
            if nextURL is None:
                return self.confirmation()
            else:
                self.request.response.redirect(nextURL)

    confirmation = ViewPageTemplateFile('login.pt')


class HTTPAuthenticationLogout(object):
    """Since HTTP Authentication really does not know about logout, we are
    simply challenging the client again."""

    implements(ILogout)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def logout(self, nextURL=None):
        """See zope.app.interfaces.security.ILogout"""
        if not isinstance(self.request.user, UnauthenticatedPrincipal):
            self.request.unauthorized("basic realm='Zope'")
        else:
            if nextURL is None:
                return self.confirmation()
            else:
                self.request.response.redirect(nextURL)
            
    confirmation = ViewPageTemplateFile('logout.pt')
