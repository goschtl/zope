##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Pluggable Authentication service implementation.

$Id: __init__.py 26176 2004-07-07 18:34:31Z jim $
"""
import time

from zope.interface import implements
from zope.exceptions import NotFoundError

from zope.app import zapi
from zope.app.location import locate

from zope.app.container.interfaces import IOrderedContainer
from zope.app.container.ordered import OrderedContainer

from zope.app.servicenames import Authentication
from zope.app.site.interfaces import ISimpleService
from zope.app.component.localservice import queryNextService

from interfaces import IPluggableAuthenticationService
from interfaces import IPrincipalSource
from btreesource import gen_key


class PluggableAuthenticationService(OrderedContainer):

    implements(IPluggableAuthenticationService, ISimpleService,
               IOrderedContainer)

    def __init__(self, earmark=None):
        self.earmark = earmark
        # The earmark is used as a token which can uniquely identify
        # this authentication service instance even if the service moves
        # from place to place within the same context chain or is renamed.
        # It is included in principal ids of principals which are obtained
        # from this auth service, so code which dereferences a principal
        # (like getPrincipal of this auth service) needs to take the earmark
        # into account. The earmark cannot change once it is assigned.  If it
        # does change, the system will not be able to dereference principal
        # references which embed the old earmark.
        OrderedContainer.__init__(self)

    def authenticate(self, request):
        """ See IAuthenticationService. """
        for ps_key, ps in self.items():
            loginView = zapi.queryView(ps, "login", request)
            if loginView is not None:
                principal = loginView.authenticate()
                if principal is not None:
                    return principal

        next = queryNextService(self, Authentication, None)
        if next is not None:
            return next.authenticate(request)

        return None

    def unauthenticatedPrincipal(self):
        # It's safe to assume that the global auth service will
        # provide an unauthenticated principal, so we won't bother.
        return None

    def unauthorized(self, id, request):
        """ See IAuthenticationService. """

        next = queryNextService(self, Authentication, None)
        if next is not None:
            return next.unauthorized(id, request)

        return None

    def getPrincipal(self, id):
        """ See IAuthenticationService.

        For this implementation, an 'id' is a string which can be
        split into a 3-tuple by splitting on tab characters.  The
        three tuple consists of (auth_service_earmark,
        principal_source_id, principal_id).

        In the current strategy, the principal sources that are members
        of this authentication service cannot be renamed; if they are,
        principal references that embed the old name will not be
        dereferenceable.

        """

        next = None

        try:
            auth_svc_earmark, principal_src_id, principal_id = id.split('\t',2)
        except (TypeError, ValueError, AttributeError):
            auth_svc_earmark, principal_src_id, principal_id = None, None, None
            next = queryNextService(self, Authentication, None)

        if auth_svc_earmark != self.earmark:
            # this is not our reference because its earmark doesnt match ours
            next = queryNextService(self, Authentication, None)

        if next is not None:
            return next.getPrincipal(id)

        source = self.get(principal_src_id)
        if source is None:
            raise NotFoundError, principal_src_id
        return source.getPrincipal(id)

    def getPrincipals(self, name):
        """ See IAuthenticationService. """

        for ps_key, ps in self.items():
            for p in ps.getPrincipals(name):
                yield p

        next = queryNextService(self, Authentication, None)
        if next is not None:
            for p in next.getPrincipals(name):
                yield p

    def addPrincipalSource(self, id, principal_source):
        """ See IPluggableAuthenticationService."""

        if not IPrincipalSource.providedBy(principal_source):
            raise TypeError("Source must implement IPrincipalSource")
        locate(principal_source, self, id)
        self[id] = principal_source        

    def removePrincipalSource(self, id):
        """ See IPluggableAuthenticationService."""
        del self[id]


def PluggableAuthenticationServiceAddSubscriber(self, event):
    """Generates an earmark if one is not provided."""

    if self.earmark is None:
        # we manufacture what is intended to be a globally unique
        # earmark if one is not provided in __init__
        myname = zapi.name(self)
        rand_id = gen_key()
        t = int(time.time())
        self.earmark = '%s-%s-%s' % (myname, rand_id, t)
