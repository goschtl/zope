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
from zope.i18n import translate
from zope.app.publisher.interfaces.http import ILogin, ILogout
from zope.app.security.interfaces import IAuthenticationService
from zope.app.security.principalregistry import UnauthenticatedPrincipal
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.proxy import removeAllProxies
from zope.app.i18n import ZopeMessageIDFactory as _


search_label = _('search-button', 'Search')

class AuthServiceSearchView(object):
    __used_for__ = IAuthenticationService

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self, name):
        html = []
        html.append('<div class="row">')
        html.append('<div class="label">')
        html.append('Search String')
        html.append('</div>')
        html.append('<div class="field">')
        html.append('<input type="text" name="%s" />' %(name+'.searchstring'))
        html.append('</div>')
        html.append('</div>')

        html.append('<br /><input type="submit" name="%s" value="%s" />'
                    % (name+'.search',
                       translate(search_label, context=self.request)))

        return '\n'.join(html)

    def results(self, name):
        if not (name+'.search' in self.request):
            return None
        searchstring = self.request[name+'.searchstring']
        if isinstance(searchstring, list):
            # Interpret as a string.
            # XXX This is a workaround for the fact that
            # SourceInputWidget generates a separate input field for
            # each principal source, so when there are multiple
            # sources, we get multiple fields that usually look
            # exactly the same.  Something needs to be redesigned.
            searchstring = ' '.join(searchstring).strip()
        return [principal.id
                for principal in self.context.getPrincipals(searchstring)]


class HTTPAuthenticationLogin(object):
    implements(ILogin)

    def login(self, nextURL=None):
        """See zope.app.security.interfaces.ILogin"""
        if isinstance(removeAllProxies(self.request.principal), \
                      UnauthenticatedPrincipal):
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
        if not isinstance(self.request.principal, UnauthenticatedPrincipal):
            self.request.unauthorized("basic realm='Zope'")
            if nextURL:
                return self.redirect()

        if nextURL is None:
            return self.confirmation()
        else:
            return self.request.response.redirect(nextURL)

    confirmation = ViewPageTemplateFile('logout.pt')

    redirect = ViewPageTemplateFile('redirect.pt')


