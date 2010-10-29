##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
""" Implementations of the session-based and cookie-based extractor and
    challenge plugins.

$Id$
"""
__docformat__ = 'restructuredtext'

import persistent
import transaction
import zope.interface
import zope.schema
from urllib import urlencode
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.browser import absoluteurl

from zope.app.component import hooks
from zope.app.container import contained
from zope.app.session.interfaces import ISession
from zope.app.authentication import interfaces


SESSION_KEY = 'z3c.tan.session.credentials'


class IBrowserFormChallenger(zope.interface.Interface):
    """A challenger that uses a browser form to collect user credentials."""

    entryPageName = zope.schema.TextLine(
        title=u'Entry Page Name',
        description=u"Name of the entry form of the TAN.",
        default=u'tanEntry.html')

    tanField = zope.schema.TextLine(
        title=u'TAN Field',
        description=u"Field name for entering the TAN to be used.",
        default=u"login.tan")


class SessionCredentialsPlugin(contained.Contained, persistent.Persistent):
    """A credentials plugin that uses Zope sessions to get/store credentials.
    """
    zope.interface.implements(
        interfaces.ICredentialsPlugin, IBrowserFormChallenger)

    entryPageName = 'tanEntry.html'
    tanField = 'login.tan'

    def __init__(self, field=None, page=None):
        if field is not None:
            self.tanField = field
        if page is not None:
            self.entryPageName = page

    def extractCredentials(self, request):
        """Extracts credentials from a session if they exist."""
        if not IHTTPRequest.providedBy(request):
            return None
        sessionData = ISession(request)[SESSION_KEY]
        tan = request.get(self.tanField, None)
        if tan:
            sessionData['tan'] = tan
        else:
            tan = sessionData.get('tan', None)
        if not tan:
            return None
        return tan

    def challenge(self, request):
        """See zope.app.authentication.interfaces.ICredentialsPlugin"""
        if not IHTTPRequest.providedBy(request):
            return False

        site = hooks.getSite()
        # We need the traversal stack to complete the 'camefrom' parameter
        stack = request.getTraversalStack()
        stack.reverse()
        # Better to add the query string, if present
        query = request.get('QUERY_STRING')

        camefrom = '/'.join([request.getURL(path_only=True)] + stack)
        if query:
            camefrom = camefrom + '?' + query
        url = '%s/@@%s?%s' % (absoluteurl.absoluteURL(site, request),
                              self.entryPageName,
                              urlencode({'camefrom': camefrom}))
        request.response.redirect(url)
        return True

    def logout(self, request):
        """See zope.app.authentication.interfaces.ICredentialsPlugin"""
        if not IHTTPRequest.providedBy(request):
            return False

        sessionData = ISession(request)[SESSION_KEY]
        sessionData['tan'] = None
        transaction.commit()
        return True

    def __repr__(self):
        return '<%s field=%r>' %(self.__class__.__name__, self.tanField)
