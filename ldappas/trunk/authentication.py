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
"""LDAP PAS Authentication plugin

$Id$
"""

from zope.app import zapi
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.interface import implements

from zope.interface import Interface
from zope.app.pas.interfaces import IAuthenticationPlugin
from ldapadapter.interfaces import ILDAPAdapter
from interfaces import ILDAPAuthentication

from ldap.filter import filter_format
from ldapadapter.exceptions import ServerDown
from ldapadapter.exceptions import InvalidCredentials
from ldapadapter.exceptions import NoSuchObject


class LDAPAuthentication(Persistent, Contained):
    """A Persistent LDAP Authentication plugin for PAS.

    An authentication plugin is configured using an LDAP Adapter that
    will be use to check user credentials that encapsulates server
    information, and additional authentication-specific informations.
    """

    implements(IAuthenticationPlugin, ILDAPAuthentication)

    adapterName = ''
    searchBase = ''
    searchScope = ''
    loginAttribute = ''
    principalIdPrefix = ''
    idAttribute = ''

    def __init__(self):
        pass

    def getLDAPAdapter(self):
        """Get the LDAP adapter according to our configuration.

        Returns None if adapter connection is configured or available.
        """
        da = zapi.queryUtility(ILDAPAdapter, self.adapterName)
        return da

    def authenticateCredentials(self, credentials):
        r"""See zope.app.pas.interfaces.IAuthenticationPlugin.

        An LDAP Adapter has to be registered, we'll use a fake one
        (registered by the test framework).

        >>> auth = LDAPAuthentication()
        >>> auth.adapterName = 'fake_ldap_adapter'
        >>> auth.searchBase = 'dc=test'
        >>> auth.searchScope = 'sub'
        >>> auth.loginAttribute = 'cn'
        >>> auth.principalIdPrefix = ''
        >>> auth.idAttribute = 'uid'
        >>> da = auth.getLDAPAdapter()
        >>> authCreds = auth.authenticateCredentials

        Incorrect credentials types are rejected.

        >>> authCreds(123) is None
        True
        >>> authCreds({'glop': 'bzz'}) is None
        True

        You cannot authenticate if the search returns several results.

        >>> len(da.connect().search('dc=test', 'sub', '(cn=many)')) > 1
        True
        >>> authCreds({'login': 'many', 'password': 'p'}) is None
        True

        You cannot authenticate if the search returns nothing.

        >>> conn = da.connect()
        >>> len(conn.search('dc=test', 'sub', '(cn=none)')) == 0
        True
        >>> authCreds({'login': 'none', 'password': 'p'}) is None
        True

        You cannot authenticate with the wrong password.

        >>> authCreds({'login': 'ok', 'password': 'hm'}) is None
        True

        Authentication succeeds if you provide the correct password.

        >>> authCreds({'login': 'ok', 'password': '42pw'})
        (u'42', {'login': 'ok'})

        The id returned comes from a configurable attribute, and can be
        prefixed so that it is unique.

        >>> auth.principalIdPrefix = 'ldap.'
        >>> auth.idAttribute = 'cn'
        >>> authCreds({'login': 'ok', 'password': '42pw'})
        (u'ldap.ok', {'login': 'ok'})

        The id attribute 'dn' can be specified to use the full dn as id.

        >>> auth.idAttribute = 'dn'
        >>> authCreds({'login': 'ok', 'password': '42pw'})
        (u'ldap.uid=42,dc=test', {'login': 'ok'})

        If the id attribute returns several values, the first one is
        used.

        >>> auth.idAttribute = 'mult'
        >>> conn.search('dc=test', 'sub', '(cn=ok)')[0][1]['mult']
        [u'm1', u'm2']
        >>> authCreds({'login': 'ok', 'password': '42pw'})
        (u'ldap.m1', {'login': 'ok'})

        Authentication fails if the id attribute is not present:

        >>> auth.idAttribute = 'nonesuch'
        >>> conn.search('dc=test', 'sub', '(cn=ok)')[0][1]['nonesuch']
        Traceback (most recent call last):
        ...
        KeyError: 'nonesuch'
        >>> authCreds({'login': 'ok', 'password': '42pw'}) is None
        True

        You cannot authenticate if the server to which the adapter
        connects is down.

        >>> da._isDown = True
        >>> authCreds({'login': 'ok', 'password': '42pw'}) is None
        True
        >>> da._isDown = False

        You cannot authenticate if the plugin has a bad configuration.

        >>> auth.searchBase = 'dc=bzzt'
        >>> authCreds({'login': 'ok', 'password': '42pw'}) is None
        True
        """

        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None

        da = self.getLDAPAdapter()
        if da is None:
            return None

        login = credentials['login']
        password = credentials['password']

        # Search for a matching entry.
        try:
            conn = da.connect()
        except ServerDown:
            return None
        filter = filter_format('(%s=%s)', (self.loginAttribute, login))
        try:
            res = conn.search(self.searchBase, self.searchScope, filter=filter)
        except NoSuchObject:
            return None
        if len(res) != 1:
            # Search returned no result or too many.
            return None
        dn, entry = res[0]

        # Find the id we'll return.
        id_attr = self.idAttribute
        if id_attr == 'dn':
            id = dn
        elif entry.get(id_attr):
            id = entry[id_attr][0]
        else:
            return None
        id = self.principalIdPrefix + id

        # Check authentication.
        try:
            conn = da.connect(dn, password)
        except InvalidCredentials:
            return None

        return id, {'login': login}
