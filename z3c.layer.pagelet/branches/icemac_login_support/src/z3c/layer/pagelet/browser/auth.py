##############################################################################
#
# Copyright (c) 2003-2009 Zope Corporation and Contributors.
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
import urllib
import zope.app.pagetemplate
import zope.app.publisher.interfaces.http
import zope.app.security.interfaces
import zope.component
import zope.i18n
import zope.i18nmessageid
import zope.interface
import zope.viewlet.interfaces
import zope.viewlet.manager
import zope.viewlet.viewlet

_ = zope.i18nmessageid.MessageFactory("z3c")


class ILoginLogoutViewletManager(zope.viewlet.interfaces.IViewletManager):
    """ViewletManager for login and logout viewlets."""


LoginLogoutViewletManager = zope.viewlet.manager.ViewletManager(
    'login-logout', ILoginLogoutViewletManager,
    bases=(zope.viewlet.manager.ConditionalViewletManager,))


def authenticated(principal):
    "Tell whether the principal is authenticated."
    unauthenticated = zope.app.security.interfaces.IUnauthenticatedPrincipal
    return not unauthenticated.providedBy(principal)


def logout_supported(request):
    "Tell whether logout is supported."
    logout = zope.app.security.interfaces.ILogoutSupported(self.request, None)
    return logout is not None


class LoginViewlet(zope.viewlet.viewlet.ViewletBase):
    """Display login link when user is not logged in."""

    @property
    def available(self):
        return not authenticated(self.request.principal)

    def render(self):
        return u'<a href="%s?nextURL=%s">%s</a>' % (
                self.viewName,
                urllib.quote(self.request.getURL()),
                zope.i18n.translate(
                    _('[Login]', default='Login'), context=self.request))


class LogoutViewlet(zope.viewlet.viewlet.ViewletBase):
    """Display logout link when user is logged in and logout is supported."""

    @property
    def available(self):
        return (
            authenticated(self.request.principal)
            and
            logout_supported(self.request))

    def render(self):
        return u'<a href="%s?nextURL=%s">%s</a>' % (
                self.viewName,
                urllib.quote(self.request.getURL()),
                zope.i18n.translate(
                    _('[Logout]', default='Logout'), context=self.request))


class HTTPAuthenticationLogin(object):

    zope.interface.implements(zope.app.publisher.interfaces.http.ILogin)

#     confirmation = zope.app.pagetemplate.ViewPageTemplateFile('login.pt')
#     failed = zope.app.pagetemplate.ViewPageTemplateFile('login_failed.pt')

    def login(self, nextURL=None):
        # we don't want to keep challenging if we're authenticated
        if zope.app.security.interfaces.IUnauthenticatedPrincipal.providedBy(
            self.request.principal):
            auth = zope.component.getUtility(
                zope.app.security.interfaces.IAuthentication)
            auth.unauthorized(self.request.principal.id, self.request)
            return self.failed()
        else:
            if nextURL is None:
                return self.confirmation()
            else:
                self.request.response.redirect(nextURL)


class HTTPAuthenticationLogout(object):
    """Since HTTP Authentication really does not know about logout, we are
    simply challenging the client again."""

    zope.interface.implements(zope.app.security.interfaces.ILogout)

#     redirect = zope.app.pagetemplate.ViewPageTemplateFile('redirect.pt')
#     confirmation = zope.app.pagetemplate.ViewPageTemplateFile('logout.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def logout(self, nextURL=None):
        if zope.app.security.interfaces.IUnauthenticatedPrincipal.providedBy(
            self.request.principal):
            pass
        else:
            auth = zope.component.getUtility(
                zope.app.security.interfaces.IAuthentication)
            zope.app.security.interfaces.ILogout(auth).logout(self.request)
            if nextURL:
                return self.redirect()
        if nextURL is None:
            return self.confirmation()
        else:
            return self.request.response.redirect(nextURL)
