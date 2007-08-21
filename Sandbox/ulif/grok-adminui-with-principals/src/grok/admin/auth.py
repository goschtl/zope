##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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

from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.principalfolder import PrincipalInfo
from zope.app.security.principalregistry import principalRegistry
from zope.interface import implements

class PrincipalRegistryAuthenticator(object):
    """An authenticator plugin, that authenticates principals against
    the global principal registry.

    """

    implements(IAuthenticatorPlugin)

    def authenticateCredentials(self, credentials):
        """Return principal info if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        principal = None
        login, password = credentials['login'], credentials['password']
        try:
            principal = principalRegistry.getPrincipalByLogin(login)
        except KeyError:
            return
        if principal and principal.validate(password):
            return PrincipalInfo(principal.id,
                                 principal.getLogin(),
                                 principal.title,
                                 principal.description)
        return

    def principalInfo(self, id):
        principal = principalRegistry.getPrincipal(id)
        if principal is None:
            return
        return PrincipalInfo(principal.id,
                             principal.getLogin(),
                             principal.title,
                             principal.description)

