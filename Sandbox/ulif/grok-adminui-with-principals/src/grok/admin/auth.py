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
from zope.app.authentication.interfaces import IQuerySchemaSearch
from zope.app.authentication.principalfolder import PrincipalInfo
from zope.app.authentication.principalfolder import ISearchSchema
from zope.app.security.principalregistry import principalRegistry
from zope.interface import implements

class PrincipalRegistryAuthenticator(object):
    """An authenticator plugin, that authenticates principals against
    the global principal registry.

    """

    implements(IAuthenticatorPlugin, IQuerySchemaSearch)

    schema = ISearchSchema

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
        return PrincipalInfo(principal.id,
                             principal.getLogin(),
                             principal.title,
                             principal.description)


    def search(self, query, start=None, batch_size=None):
        """Search through this principal provider.
        """
        search = query.get('search')
        if search is None:
            return
        search = search.lower()
        n = 1
        values = [x for x in principalRegistry.getPrincipals('')
                  if x is not None]
        for i, value in enumerate(values):
            if (search in value.title.lower() or
                search in value.description.lower() or
                search in value.getLogin().lower()):
                if not ((start is not None and i < start)
                        or (batch_size is not None and n > batch_size)):
                    n += 1
                    yield value.__name__
