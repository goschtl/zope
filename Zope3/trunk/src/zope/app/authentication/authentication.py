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

from zope import component

from zope.app.security.interfaces import IAuthentication
from zope.app.utility.utility import queryNextUtility
from zope.app.container.contained import Contained
from zope.app.utility.interfaces import ILocalUtility
from zope.app.location.interfaces import ILocation

from zope.app.authentication.interfaces import IExtractionPlugin
from zope.app.authentication.interfaces import IAuthenticationPlugin
from zope.app.authentication.interfaces import IChallengePlugin
from zope.app.authentication.interfaces import IPrincipalFactoryPlugin
from zope.app.authentication.interfaces \
     import IUnauthenticatedPrincipalFactoryPlugin
from zope.app.authentication.interfaces import IPrincipalSearchPlugin
from zope.app.authentication.interfaces import IPluggableAuthentication

class PluggableAuthentication(object):

    zope.interface.implements(
        IPluggableAuthentication, IAuthentication, ISourceQueriables)

    authenticators = extractors = challengers = factories = searchers = ()

    def __init__(self, prefix=''):
        self.prefix = prefix

    def authenticate(self, request):
        authenticators = [component.queryUtility(IAuthenticationPlugin, name)
                          for name in self.authenticators]
        for extractor in self.extractors:
            extractor = component.queryUtility(IExtractionPlugin, extractor)
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
            factory = component.queryUtility(IPrincipalFactoryPlugin,
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
            searcher = component.queryUtility(IPrincipalSearchPlugin, searcher)
            if searcher is None:
                continue

            info = searcher.principalInfo(id)
            if info is None:
                continue

            return self._create('createFoundPrincipal', self.prefix+id, info)

        return self._delegate('getPrincipal', self.prefix+id)

    def getQueriables(self):
        for searcher_id in self.searchers:
            searcher = component.queryUtility(IPrincipalSearchPlugin,
                                              searcher_id)
            yield searcher_id, searcher
        

    def unauthenticatedPrincipal(self):
        factory = component.queryUtility(
            IUnauthenticatedPrincipalFactoryPlugin)
        if factory is not None:
            return factory.createUnauthenticatedPrincipal()
        return None

    def unauthorized(self, id, request):
        protocol = None

        for challenger in self.challengers:
            challenger = component.queryUtility(IChallengePlugin, challenger)
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

class LocalPluggableAuthentication(PluggableAuthentication,
                                   Persistent, Contained):
    zope.interface.implements(IPluggableAuthentication,
                              ILocation, ILocalUtility)
