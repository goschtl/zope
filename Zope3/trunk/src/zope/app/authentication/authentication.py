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
            return (next is not None) and next.getPrincipal(id) or None
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
            authplugin = component.queryUtility(
                interfaces.IAuthenticatorPlugin,
                name, context=self)
            if authplugin is None:
                continue
            queriable = interfaces.IQueriableAuthenticator(authplugin, None)
            if queriable is None:
                continue
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
