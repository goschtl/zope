##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Login and Logout screens

$Id$
"""
from zope.interface import implements
from zope.app.publisher.interfaces.http import ILogin, ILogout
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.pagetemplate import ViewPageTemplateFile

class HTTPAuthenticationLogin(object):
    implements(ILogin)

    def login(self, nextURL=None):
        """See zope.app.security.interfaces.ILogin"""
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            self.request.unauthorized("basic realm='Zope'")
            return self.failed()
        else:
            if nextURL is None:
                return self.confirmation()
            else:
                self.request.response.redirect(nextURL)

    confirmation = ViewPageTemplateFile('login.pt')

    failed = ViewPageTemplateFile('login_failed.pt')


class HTTPAuthenticationLogout(object):
    """Since HTTP Authentication really does not know about logout, we are
    simply challenging the client again."""

    implements(ILogout)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def logout(self, nextURL=None):
        """See zope.app.security.interfaces.ILogout"""
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            self.request.unauthorized("basic realm='Zope'")
            if nextURL:
                return self.redirect()

        if nextURL is None:
            return self.confirmation()
        else:
            return self.request.response.redirect(nextURL)

    confirmation = ViewPageTemplateFile('logout.pt')

    redirect = ViewPageTemplateFile('redirect.pt')


