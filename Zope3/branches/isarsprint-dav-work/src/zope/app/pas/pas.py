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
"""Pluggable authentication service implementation

$Id$
"""

from zope.event import notify
import zope.interface
import zope.schema

from zope.app import zapi

from zope.app.pas import vocabularies, interfaces
from zope.app.pas.interfaces import IExtractionPlugin
from zope.app.pas.interfaces import IAuthenticationPlugin
from zope.app.pas.interfaces import IChallengePlugin
from zope.app.pas.interfaces import IPrincipalFactoryPlugin
from zope.app.pas.interfaces import IPrincipalSearchPlugin


class IPAS(zope.interface.Interface):
    """Pluggable Authentication Service
    """
    
    extractors = zope.schema.Tuple(
        title=u"Credential Extractors",
        value_type = zope.schema.Choice(
            vocabulary = vocabularies.UtilityNames(IExtractionPlugin)),
        default=(),
        )
    
    authenticators = zope.schema.Tuple(
        title=u"Authenticators",
        value_type = zope.schema.Choice(
            vocabulary = vocabularies.UtilityNames(IAuthenticationPlugin)),
        default=(),
        )
    
    challengers = zope.schema.Tuple(
        title=u"Challengers",
        value_type = zope.schema.Choice(
            vocabulary = vocabularies.UtilityNames(IChallengePlugin)),
        default=(),
        )
    
    factories = zope.schema.Tuple(
        title=u"Principal Factories",
        value_type = zope.schema.Choice(
            vocabulary = vocabularies.UtilityNames(IPrincipalFactoryPlugin)),
        default=(),
        )
    
    searchers = zope.schema.Tuple(
        title=u"Search Plugins",
        value_type = zope.schema.Choice(
            vocabulary = vocabularies.UtilityNames(IPrincipalSearchPlugin)),
        default=(),
        )
    
class PAS:

    zope.interface.implements(IPAS)

    authenticators = extractors = challengers = factories = search = ()

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
            return
        id = id[len(self.prefix):]

        for searcher in self.searchers:
            searcher = zapi.queryUtility(IPrincipalSearchPlugin, searcher)
            if searcher is None:
                continue
        
            info = searcher.get(id)
            if info is None:
                continue

            return self._create('createFoundPrincipal', self.prefix+id, info)

    def unauthenticatedPrincipal(self):
        pass

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
                        break
                    elif protocol is None:
                        protocol = challenger_protocol

        # XXX Fallback code.  This will call unauthorized on higher-level
        # authentication services.
        
