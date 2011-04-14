##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""query views for shared sources

$Id$
"""
import zope.app.form.browser.interfaces
import zope.publisher.interfaces.browser

from zope import component, interface, i18n
from zope.app import zapi
from zope.app import pagetemplate
from zope.schema.interfaces import ITitledTokenizedTerm

from zc.security.i18n import _
from zc.security.interfaces import ISimpleUserSource
from zc.security.interfaces import ISimpleUserSearch
from zc.security.interfaces import ISimpleGroupSource
from zc.security.interfaces import ISimpleGroupSearch
from zc.security.interfaces import ISimplePrincipalSource
from zc.security.interfaces import ISimplePrincipalSearch

SEARCH_FIELD_NAME = _('source_query_view_search', 'Search String')
SEARCH_BUTTON = _('search-button', 'Search')

class SimplePrincipalSourceQueryBaseView(object):
    interface.implements(zope.app.form.browser.interfaces.ISourceQueryView)

    def __init__(self, source, request):
        self.context = source
        self.request = request

    _render = pagetemplate.ViewPageTemplateFile('queryview.pt')
    def render(self, name):
        field_name = name + '.searchstring'
        self.searchstring = self.request.get(field_name)
        return self._render(field_name = field_name,
                            button_name = name + '.search')

    def results(self, name):
        if not (name+'.search' in self.request):
            return None
        searchstring = self.request[name+'.searchstring']
        if not searchstring:
            return None
        principals = zapi.principals()
        return self.search(principals, searchstring, 0, 999999999999)

    def search(self, principals, searchstring, start, size):
        raise NotImplementedError('override in subclasses')


class SimpleUserSourceQueryView(SimplePrincipalSourceQueryBaseView):

    component.adapts(ISimpleUserSource,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def search(self, principals, searchstring, start, size):
        search = ISimpleUserSearch(principals)
        return search.searchUsers(searchstring, start, size)


class SimpleGroupSourceQueryView(SimplePrincipalSourceQueryBaseView):

    component.adapts(ISimpleGroupSource,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def search(self, principals, searchstring, start, size):
        search = ISimpleGroupSearch(principals)
        return search.searchGroups(searchstring, start, size)


class SimplePrincipalSourceQueryView(SimplePrincipalSourceQueryBaseView):

    component.adapts(ISimplePrincipalSource,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def search(self, principals, searchstring, start, size):
        search = ISimplePrincipalSearch(principals)
        return search.searchPrincipals(searchstring, start, size)


class Term:
    zope.interface.implements(ITitledTokenizedTerm)

    def __init__(self, title, token):
        self.title = title
        self.token = token


class SourceTerms:
    """Term and value support needed by query widgets."""

    zope.interface.implements(zope.app.form.browser.interfaces.ITerms)
    component.adapts(ISimplePrincipalSource,
                     zope.publisher.interfaces.browser.IBrowserRequest)

    def __init__(self, source, request):
        pass

    def getTerm(self, value):
        principal = zapi.principals().getPrincipal(value)
        token = value.encode('base64').strip()
        return Term(principal.title, token)

    def getValue(self, token):
        return token.decode('base64')
