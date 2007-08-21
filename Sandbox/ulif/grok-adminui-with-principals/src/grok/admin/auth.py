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

from zope.app.authentication.principalfolder import PrincipalFolder
from zope.app.authentication.principalfolder import PrincipalInfo
from zope.app.security.principalregistry import principalRegistry

class GrokAuthenticator(PrincipalFolder):
    """A PrincipalFolder with fallback that asks also the root authentication.

    This special principal folder can be used as an authenticator,
    that is able to also authenticate against the principals defined
    in site.zcml.
    """

    def authenticateCredentials(self, credentials):
        """Return principal info if credentials can be authenticated
        """
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        # We shadow principals defined in site.zcml.
        result = PrincipalFolder.authenticateCredentials(self, credentials)
        if result is not None:
            return result

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
        result = PrincipalFolder.principalInfo(self, id)
        if result is not None:
            return result
        principal = principalRegistry.getPrincipal(id)
        return PrincipalInfo(principal.id,
                             principal.getLogin(),
                             principal.title,
                             principal.description)
        return result

