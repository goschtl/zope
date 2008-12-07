##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

    This authenticator does not support own prefixes, because the
    prefix of its principals is already defined in another place
    (site.zcml). Therefore we get and give back IDs as they are.
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
            return PrincipalInfo(u''+principal.id,
                                 principal.getLogin(),
                                 principal.title,
                                 principal.description)
        return

    def principalInfo(self, id):
        principal = principalRegistry.getPrincipal(id)
        if principal is not None:
            return PrincipalInfo(u''+principal.id,
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
        values.sort(cmp=lambda x,y: cmp(str(x.id), str(y.id)))
        for i, value in enumerate(values):
            if (search in value.id.lower() or
                search in value.title.lower() or
                search in value.description.lower() or
                search in value.getLogin().lower()):
                if not ((start is not None and i < start)
                        or (batch_size is not None and n > batch_size)):
                    n += 1
                    yield u''+value.__name__
