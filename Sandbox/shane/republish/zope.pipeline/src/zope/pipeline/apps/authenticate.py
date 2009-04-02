##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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

from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IFallbackUnauthenticatedPrincipal
from zope.component import getGlobalSiteManager
from zope.security.management import endInteraction
from zope.security.management import newInteraction

from zope.pipeline.envkeys import REQUEST_KEY
from zope.pipeline.envkeys import TRAVERSAL_HOOKS_KEY


class Authenticator(object):
    """WSGI app that hooks into Zope-based authentication.

    The WSGI environment must contain 'zope.pipeline.request'.
    Adds a traversal hook if local authentication is enabled.
    """

    def __init__(self, next_app, local_auth=True):
        self.next_app = next_app
        self.local_auth = local_auth

    def __call__(self, environ, start_response):
        request = environ[REQUEST_KEY]
        auth = getGlobalSiteManager().getUtility(IAuthentication)
        principal = auth.authenticate(request)
        if principal is None:
            if self.local_auth:
                hooks = environ.setdefault(TRAVERSAL_HOOKS_KEY, [])
                hooks.append(placeful_auth)
            principal = auth.unauthenticatedPrincipal()
            if principal is None:
                # Get the fallback unauthenticated principal
                principal = getUtility(IFallbackUnauthenticatedPrincipal)
        request.principal = principal

        newInteraction(request)
        try:
            return self.next_app(environ, start_response)
        finally:
            endInteraction()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, repr(self.next_app))


def placeful_auth(request, ob):
    """Traversal hook that tries to authenticate in a context"""

    if not IUnauthenticatedPrincipal.providedBy(request.principal):
        # We've already got an authenticated user. There's nothing to do.
        # Note that beforeTraversal guarentees that user is not None.
        return

    if not ISite.providedBy(ob):
        # We won't find an authentication utility here, so give up.
        return

    sm = removeSecurityProxy(ob).getSiteManager()

    auth = sm.queryUtility(IAuthentication)
    if auth is None:
        # No auth utility here
        return

    # Try to authenticate against the auth utility
    principal = auth.authenticate(request)
    if principal is None:
        principal = auth.unauthenticatedPrincipal()
        if principal is None:
            # nothing to do here
            return

    request.setPrincipal(principal)
