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
import urllib
from zope.interface import implements
from zope.i18n import translate
from zope.app.zapi import getName, getPath
from zope.app.publisher.interfaces.http import ILogin, ILogout
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.proxy import removeAllProxies
from zope.app.i18n import ZopeMessageIDFactory as _


search_label = _('search-button', 'Search')

class AuthUtilitySearchView(object):
    __used_for__ = IAuthentication

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def render(self, name):
        sourcename = 'principals.zcml'
        html = []

        # add sub title for source search field
        html.append('<h4 i18n:translate="">%s</h4>' % sourcename)
        # start row for search fields
        html.append('<div class="row">')
        html.append('<div class="label">')
        html.append('Search String')
        html.append('</div>')
        html.append('<div class="field">')
        html.append('<input type="text" name="%s" />' %(name+'.searchstring'))
        html.append('</div>')
        html.append('</div>')

        # add search button for search fields
        html.append('<div class="row">')
        html.append('<div class="field">')
        html.append('<input type="submit" name="%s" value="%s" />'
                    % (name+'.search',
                       translate(search_label, context=self.request)))
        html.append('</div>')

        # end row
        html.append('</div>')

        return '\n'.join(html)

    def results(self, name):
        if not (name+'.search' in self.request):
            return None
        searchstring = self.request[name+'.searchstring']
        return [principal.id
                for principal in self.context.getPrincipals(searchstring)]


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


class LoginLogout:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if IUnauthenticatedPrincipal.providedBy(self.request.principal):
            page = '@@login.html'
            label = _('[Login]')
        else:
            page = '@@logout.html'
            label = _('[Logout]')
        return '<a href="%s?nextURL=%s">%s</a>' % (
            page, urllib.quote(self.request.getURL()), label)
