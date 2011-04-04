##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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

from urllib import quote_plus

from openid.consumer.consumer import Consumer
from openid.consumer.consumer import SUCCESS
from openid.store.memstore import MemoryStore
from persistent import Persistent
from persistent.mapping import PersistentMapping
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import PrincipalLookupError
from zope.component import getMultiAdapter
from zope.traversing.browser import absoluteURL
from zope.interface import implements
from zope.location import Location
from zope.publisher.interfaces import Redirect
from zope.session.interfaces import ISession
from zope.security.interfaces import IPrincipal

from zc.openid.interfaces import AuthenticationFailed
from zc.openid.interfaces import IOpenIDConsumer

PACKAGE = 'zc.openid'
PRINCIPAL = 'principal'
CONSUMER = 'consumer'

# XXX This needs to be in ZODB.
store = MemoryStore()


class OpenIDPrincipal(object):
    implements(IPrincipal)

    description = u"User authenticated via OpenID"

    def __init__(self, principal_id):
        self.id = self.title = principal_id


class OpenIDConsumer(Persistent, Location):
    implements(IOpenIDConsumer)

    single_provider = None
    _consumer_class = Consumer

    def authenticate(self, request):
        """Identify a principal for a request.

        If a principal can be identified, then return the
        principal. Otherwise, return None.
        """
        #if not IBrowserRequest.providedBy(request):
        #    raise NotImplementedError(
        #        "only browser requests are supported by OpenIDConsumer")
        session = ISession(request)[PACKAGE]
        return session.get(PRINCIPAL, None)

    def _get_consumer(self, request):
        session = ISession(request)[PACKAGE]
        consumer_session_data = session.get(CONSUMER)
        if consumer_session_data is None:
            consumer_session_data = PersistentMapping()
            session[CONSUMER] = consumer_session_data
        else:
            consumer_session_data._p_changed = True
        return self._consumer_class(consumer_session_data, store)

    def _get_view_url(self, request, name):
        site = getSite()
        base = absoluteURL(site, request)
        res = "%s/@@openid/%s" % (base, name)
        next_url = request.get('nextURL')
        if next_url:
            res += '?nextURL=' + quote_plus(next_url)
        return res

    def login(self, request, identity_url=None):
        if self.single_provider:
            # override
            identity_url = self.single_provider
        if identity_url:
            consumer = self._get_consumer(request)
            auth_req = consumer.begin(identity_url)
            site = getSite()
            realm = absoluteURL(site, request)
            url = auth_req.redirectURL(
                realm, self._get_view_url(request, 'complete'))
        else:
            url = self._get_view_url(request, 'choose_identity')
        request.response.redirect(url)

    def complete(self, request):
        app_url = self._get_view_url(request, 'complete')
        consumer = self._get_consumer(request)
        resp = consumer.complete(request.form, app_url)
        if resp.status != SUCCESS:
            raise AuthenticationFailed(resp)
        else:
            session = ISession(request)[PACKAGE]
            session[PRINCIPAL] = OpenIDPrincipal(resp.identity_url)
            next_url = request.get('nextURL')
            if not next_url:
                next_url = absoluteURL(getSite(), request)
            request.response.redirect(next_url)

    def unauthenticatedPrincipal(self):
        """Return the unauthenticated principal, if one is defined.

        Return None if no unauthenticated principal is defined.

        The unauthenticated principal must be an IUnauthenticatedPrincipal.
        """
        return None

    def unauthorized(self, principal_id, request):
        """Signal an authorization failure.

        This method is called when an auhorization problem
        occurs. It can perform a variety of actions, such
        as issuing an HTTP authentication challenge or
        displaying a login interface.

        Note that the authentication utility nearest to the
        requested resource is called. It is up to
        authentication utility implementations to
        collaborate with utilities higher in the object
        hierarchy.

        If no principal has been identified, id will be
        None.
        """
        self.login(request)

    def getPrincipal(self, id):
        """Get principal meta-data.

        Returns an object of type IPrincipal for the given principal
        id. A PrincipalLookupError is raised if the principal cannot be
        found.

        Note that the authentication utility nearest to the requested
        resource is called. It is up to authentication utility
        implementations to collaborate with utilities higher in the
        object hierarchy.
        """
        raise PrincipalLookupError()
