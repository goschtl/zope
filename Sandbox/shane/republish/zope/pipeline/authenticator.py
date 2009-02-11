
from zope.component import getGlobalSiteManager
from zope.interface import adapts
from zope.interface import implements
from zope.publisher.interfaces import IWSGIApplication
from zope.security.management import newInteraction
from zope.security.management import endInteraction

from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import IFallbackUnauthenticatedPrincipal


class Authenticator(object):
    """WSGI app that hooks into Zope-based authentication.

    The WSGI environment must contain 'zope.request'.
    """
    implements(IWSGIApplication)
    adapts(IWSGIApplication)

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = environ['zope.request']
        auth = getGlobalSiteManager().getUtility(IAuthentication)
        principal = auth.authenticate(request)
        if principal is None:
            request.traversal_hooks.append(placeful_auth)
            principal = auth.unauthenticatedPrincipal()
            if principal is None:
                # Get the fallback unauthenticated principal
                principal = getUtility(IFallbackUnauthenticatedPrincipal)
        request.principal = principal

        newInteraction(request)
        try:
            return self.app(environ, start_response)
        finally:
            endInteraction()


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
