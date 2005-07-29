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

from zope import component
from zope.schema.interfaces import ISourceQueriables
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError
from zope.app.location.interfaces import ILocation
from zope.app.component import queryNextUtility
from zope.app.component.site import SiteManagementFolder

from zope.app.authentication import interfaces

class PluggableAuthentication(SiteManagementFolder):

    zope.interface.implements(
        IAuthentication,
        interfaces.IPluggableAuthentication,
        ISourceQueriables)

    authenticatorPlugins = ()
    credentialsPlugins = ()

    def __init__(self, prefix=''):
        super(PluggableAuthentication, self).__init__()
        self.prefix = prefix

    def authenticate(self, request):
        authenticatorPlugins = [
            component.queryUtility(interfaces.IAuthenticatorPlugin,
                                  name, context=self)
            for name in self.authenticatorPlugins]
        for name in self.credentialsPlugins:
            credplugin = component.queryUtility(
                interfaces.ICredentialsPlugin, name, context=self)
            if credplugin is None:
                continue
            credentials = credplugin.extractCredentials(request)
            for authplugin in authenticatorPlugins:
                if authplugin is None:
                    continue
                info = authplugin.authenticateCredentials(credentials)
                if info is None:
                    continue
                principal = component.getMultiAdapter((info, request),
                    interfaces.IAuthenticatedPrincipalFactory)(self)
                principal.id = self.prefix + info.id
                return principal
        return None

    def getPrincipal(self, id):
        if not id.startswith(self.prefix):
            next = queryNextUtility(self, IAuthentication)
            if next is None:
                raise PrincipalLookupError(id)
            return next.getPrincipal(id)
        id = id[len(self.prefix):]
        for name in self.authenticatorPlugins:
            authplugin = component.queryUtility(
                interfaces.IAuthenticatorPlugin, name, context=self)
            if authplugin is None:
                continue
            info = authplugin.principalInfo(id)
            if info is None:
                continue
            principal = interfaces.IFoundPrincipalFactory(info)(self)
            principal.id = self.prefix + info.id
            return principal
        next = queryNextUtility(self, IAuthentication)
        if next is not None:
            return next.getPrincipal(self.prefix + id)
        raise PrincipalLookupError(id)

    def getQueriables(self):
        for name in self.authenticatorPlugins:
            authplugin = component.queryUtility(interfaces.IAuthenticatorPlugin,
                name, context=self)
            if authplugin is None:
                continue
            queriable = component.queryMultiAdapter((authplugin, self),
                interfaces.IQuerySchemaSearch)
            if queriable is not None:
                yield name, queriable

    def unauthenticatedPrincipal(self):
        return None

    def unauthorized(self, id, request):
        challengeProtocol = None

        for name in self.credentialsPlugins:
            credplugin = component.queryUtility(interfaces.ICredentialsPlugin,
                                                name)
            if credplugin is None:
                continue
            protocol = getattr(credplugin, 'challengeProtocol', None)
            if challengeProtocol is None or protocol == challengeProtocol:
                if credplugin.challenge(request):
                    if protocol is None:
                        return
                    elif challengeProtocol is None:
                        challengeProtocol = protocol

        if challengeProtocol is None:
            next = queryNextUtility(self, IAuthentication)
            if next is not None:
                next.unauthorized(id, request)

    def logout(self, request):
        challengeProtocol = None

        for name in self.credentialsPlugins:
            credplugin = component.queryUtility(interfaces.ICredentialsPlugin,
                                                name)
            if credplugin is None:
                continue
            protocol = getattr(credplugin, 'challengeProtocol', None)
            if challengeProtocol is None or protocol == challengeProtocol:
                if credplugin.logout(request):
                    if protocol is None:
                        return
                    elif challengeProtocol is None:
                        challengeProtocol = protocol

        if challengeProtocol is None:
            next = queryNextUtility(self, IAuthentication)
            if next is not None:
                next.logout(request)


class PluggableAuthenticationQueriable(object):
    """Performs principal searches on behald of a PAU.

    Delegates the search to the authenticator but prepends the PAU prefix to
    the resulting principal IDs.
    """
    component.adapts(
        interfaces.IQuerySchemaSearch,
        interfaces.IPluggableAuthentication)

    zope.interface.implements(interfaces.IQuerySchemaSearch, ILocation)

    def __init__(self, queriable, pau):
        self.__parent__ = pau
        self.__name__ = ''
        self.queriable = queriable
        self.pau = pau
        self.schema = queriable.schema

    def search(self, query, start=None, batch_size=None):
        for id in self.queriable.search(query, start, batch_size):
            yield self.pau.prefix + id
