##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Pluggable Authentication Utility implementation

$Id$
"""
from zope.event import notify
import zope.interface
import zope.schema
from persistent import Persistent

from zope.schema.interfaces import ISourceQueriables

from zope.app import zapi

from zope.app.security.interfaces import IAuthentication
from zope.app.component import queryNextUtility
from zope.app.container.contained import Contained
from zope.app.component.interfaces import ILocalUtility
from zope.app.location.interfaces import ILocation

from zope.app.pau import interfaces
from zope.app.pau.interfaces import IExtractionPlugin
from zope.app.pau.interfaces import IAuthenticationPlugin
from zope.app.pau.interfaces import IChallengePlugin
from zope.app.pau.interfaces import IPrincipalFactoryPlugin
from zope.app.pau.interfaces import IPrincipalSearchPlugin


class IPAU(zope.interface.Interface):
    """Pluggable Authentication Utility
    """

    extractors = zope.schema.List(
        title=u"Credential Extractors",
        value_type = zope.schema.Choice(vocabulary='ExtractionPlugins'),
        default=[],
        )

    authenticators = zope.schema.List(
        title=u"Authenticators",
        value_type = zope.schema.Choice(vocabulary='AuthenticationPlugins'),
        default=[],
        )

    challengers = zope.schema.List(
        title=u"Challengers",
        value_type = zope.schema.Choice(vocabulary='ChallengePlugins'),
        default=[],
        )

    factories = zope.schema.List(
        title=u"Principal Factories",
        value_type = zope.schema.Choice(vocabulary='PrincipalFactoryPlugins'),
        default=[],
        )

    searchers = zope.schema.List(
        title=u"Search Plugins",
        value_type = zope.schema.Choice(vocabulary='PrincipalSearchPlugins'),
        default=[],
        )

class PAU(object):

    zope.interface.implements(IPAU, IAuthentication, ISourceQueriables)

    authenticators = extractors = challengers = factories = searchers = ()

    def __init__(self, prefix=''):
        self.prefix = prefix

    def authenticate(self, request):
        authenticators = [zapi.queryUtility(IAuthenticationPlugin, name)
                          for name in self.authenticators]
        for extractor in self.extractors:
            extractor = zapi.queryUtility(IExtractionPlugin, extractor)
            if extractor is None:
                continue
            credentials = extractor.extractCredentials(request)
            for authenticator in authenticators:
                if authenticator is None:
                    continue
                authenticated = authenticator.authenticateCredentials(
                    credentials)
                if authenticated is None:
                    continue

                id, info = authenticated
                return self._create('createAuthenticatedPrincipal',
                                    self.prefix+id, info, request)
        return None

    def _create(self, meth, *args):
        # We got some data, lets create a user
        for factory in self.factories:
            factory = zapi.queryUtility(IPrincipalFactoryPlugin,
                                        factory)
            if factory is None:
                continue

            principal = getattr(factory, meth)(*args)
            if principal is None:
                continue

            return principal

    def getPrincipal(self, id):
        if not id.startswith(self.prefix):
            return self._delegate('getPrincipal', id)
        id = id[len(self.prefix):]

        for searcher in self.searchers:
            searcher = zapi.queryUtility(IPrincipalSearchPlugin, searcher)
            if searcher is None:
                continue

            info = searcher.principalInfo(id)
            if info is None:
                continue

            return self._create('createFoundPrincipal', self.prefix+id, info)

        return self._delegate('getPrincipal', self.prefix+id)

    def getQueriables(self):
        for searcher_id in self.searchers:
            searcher = zapi.queryUtility(IPrincipalSearchPlugin, searcher_id)
            yield searcher_id, searcher
        

    def unauthenticatedPrincipal(self):
        return None

    def unauthorized(self, id, request):
        protocol = None

        for challenger in self.challengers:
            challenger = zapi.queryUtility(IChallengePlugin, challenger)
            if challenger is None:
                continue # skip non-existant challengers

            challenger_protocol = getattr(challenger, 'protocol', None)
            if protocol is None or challenger_protocol == protocol:
                if challenger.challenge(request, request.response):
                    if challenger_protocol is None:
                        return
                    elif protocol is None:
                        protocol = challenger_protocol

        if protocol is None:
            self._delegate('unauthorized', id, request)

    def _delegate(self, meth, *args):
        # delegate to next AU
        next = queryNextUtility(self, IAuthentication)
        if next is None:
            return None
        return getattr(next, meth)(*args)

    # BBB
    def getPrincipals(self, name):
        import warnings
        warnings.warn(
            "The getPrincipals method has been deprecicated. "
            "It will be removed in Zope X3.3. "
            "You'll find no principals here.",
            DeprecationWarning, stacklevel=2)
        return ()

class LocalPAU(PAU, Persistent, Contained):
    zope.interface.implements(IPAU, ILocation, ILocalUtility)
