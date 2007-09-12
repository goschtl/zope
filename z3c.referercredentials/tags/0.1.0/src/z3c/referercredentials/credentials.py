##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""HTTP Referer Credentials interfaces

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import transaction
import urllib2
import zope.interface
from zope.app.component import hooks
from zope.app.container import contained
from zope.app.session.interfaces import ISession
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.browser import absoluteURL

from z3c.referercredentials import interfaces

class HTTPRefererCredentials(persistent.Persistent, contained.Contained):
    zope.interface.implements(interfaces.IHTTPRefererCredentials)

    sessionKey = 'z3c.referercredentials'
    allowedHosts = ('localhost',)
    credentials = None
    challengeView = 'unauthorized.html'

    def extractCredentials(self, request):
        """See zope.app.authentication.interfaces.ICredentialsPlugin"""
        # Step 0: This credentials plugin only works for HTTP request
        if not IHTTPRequest.providedBy(request):
            return None
        # Step 1: If the referer hostname matches
        url = request.getHeader('Referer', '')
        host = urllib2.splithost(urllib2.splittype(url)[-1])[0]
        if host in self.allowedHosts:
            ISession(request)[self.sessionKey]['authenticated'] = True
        # Step 2: If the "authenticated" flag is set, return the
        #         pre-determined credentials."
        if ISession(request)[self.sessionKey].get('authenticated'):
            return self.credentials
        return None

    def challenge(self, request):
        """See zope.app.authentication.interfaces.ICredentialsPlugin"""
        # Step 0: This credentials plugin only works for HTTP request
        if not IHTTPRequest.providedBy(request):
            return False
        # Step 1: Produce a URL and redirect to it
        site = hooks.getSite()
        url = '%s/@@%s' % (absoluteURL(site, request), self.challengeView)
        request.response.redirect(url)
        return True

    def logout(self, request):
        """See zope.app.authentication.interfaces.ICredentialsPlugin"""
        # Step 0: This credentials plugin only works for HTTP request
        if not IHTTPRequest.providedBy(request):
            return False
        # Step 1: Delete the session variable.
        del ISession(request)[self.sessionKey]['authenticated']
        transaction.commit()
        return True
