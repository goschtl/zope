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
from zope.schema import TextLine
from zope.app.pas.interfaces import IAuthenticationPlugin
from zope.app.pas.interfaces import IQuerySchemaSearch
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

    implements(ILDAPAuthentication, IAuthenticationPlugin, IQuerySchemaSearch)

    adapterName = ''
    searchBase = ''
    searchScope = ''
    loginAttribute = ''
    principalIdPrefix = ''
    idAttribute = ''
    titleAttribute = ''

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
        >>> auth.titleAttribute = 'sn'
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

        >>> id, info = authCreds({'login': 'ok', 'password': '42pw'})
        >>> id, info['login'], info['title'], info['description']
        (u'42', u'ok', u'the question', u'the question')

        The id returned comes from a configurable attribute, and can be
        prefixed so that it is unique.

        >>> auth.principalIdPrefix = 'ldap.'
        >>> auth.idAttribute = 'cn'
        >>> authCreds({'login': 'ok', 'password': '42pw'})[0]
        u'ldap.ok'

        The id attribute 'dn' can be specified to use the full dn as id.

        >>> auth.idAttribute = 'dn'
        >>> authCreds({'login': 'ok', 'password': '42pw'})[0]
        u'ldap.uid=42,dc=test'

        If the id attribute returns several values, the first one is
        used.

        >>> auth.idAttribute = 'mult'
        >>> conn.search('dc=test', 'sub', '(cn=ok)')[0][1]['mult']
        [u'm1', u'm2']
        >>> authCreds({'login': 'ok', 'password': '42pw'})[0]
        u'ldap.m1'

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
        except (ServerDown, InvalidCredentials):
            return None

        return id, self.getInfoFromEntry(dn, entry)

    def getInfoFromEntry(self, dn, entry):
        try:
            title = entry[self.titleAttribute][0]
        except (KeyError, IndexError):
            title = dn
        return {'login': entry[self.loginAttribute][0],
                'title': title,
                'description': title,
                }

    def get(self, id):
        """See zope.app.pas.interfaces.IPrincipalSearchPlugin.

        >>> auth = LDAPAuthentication()
        >>> auth.adapterName = 'fake_ldap_adapter'
        >>> auth.loginAttribute = 'cn'
        >>> auth.principalIdPrefix = 'ldap.'
        >>> auth.idAttribute = 'uid'
        >>> auth.titleAttribute = 'sn'

        If the id is not in this plugin, return nothing.

        >>> auth.get('42') is None
        True

        Otherwise return the info if we have it.

        >>> auth.get('ldap.123') is None
        True
        >>> info = auth.get('ldap.42')
        >>> info['login'], info['title'], info['description']
        (u'ok', u'the question', u'the question')
        """
        if not id.startswith(self.principalIdPrefix):
            return None
        id = id[len(self.principalIdPrefix):]

        da = self.getLDAPAdapter()
        if da is None:
            return None
        try:
            conn = da.connect()
        except ServerDown:
            return None

        filter = filter_format('(%s=%s)', (self.idAttribute, id))
        try:
            res = conn.search(self.searchBase, self.searchScope,
                              filter=filter)
        except NoSuchObject:
            return None

        if len(res) != 1:
            # Search returned no result or too many.
            return None
        dn, entry = res[0]

        return self.getInfoFromEntry(dn, entry)

    class schema(Interface):
        """See of zope.app.pas.interfaces.IQuerySchemaSearch.
        """
        uid = TextLine(
            title=u'uid',
            required=False)
        cn = TextLine(
            title=u'cn',
            required=False)
        givenName = TextLine(
            title=u'givenName',
            required=False)
        sn = TextLine(
            title=u'sn',
            required=False)

    def search(self, query, start=None, batch_size=None):
        """See zope.app.pas.interfaces.IQuerySchemaSearch.

        >>> auth = LDAPAuthentication()
        >>> auth.adapterName = 'fake_ldap_adapter'
        >>> auth.loginAttribute = 'cn'
        >>> auth.principalIdPrefix = 'ldap.'
        >>> auth.idAttribute = 'uid'

        An empty search returns everything.

        >>> auth.search({})
        [u'ldap.1', u'ldap.2', u'ldap.42']

        A search for a specific entry returns it.

        >>> auth.search({'cn': 'many'})
        [u'ldap.1', u'ldap.2']

        You can have multiple search criteria, they are ANDed.

        >>> auth.search({'cn': 'many', 'sn': 'mr2'})
        [u'ldap.2']

        Batching can be used to restrict the result range.

        >>> auth.search({}, start=1)
        [u'ldap.2', u'ldap.42']
        >>> auth.search({}, start=1, batch_size=1)
        [u'ldap.2']
        >>> auth.search({}, batch_size=2)
        [u'ldap.1', u'ldap.2']
        """
        da = self.getLDAPAdapter()
        if da is None:
            return ()
        try:
            conn = da.connect()
        except ServerDown:
            return ()

        # Build the filter based on the query
        filter_elems = []
        for key, value in query.items():
            if not value:
                continue
            filter_elems.append(filter_format('(%s=*%s*)',
                                              (key, value)))
        filter = ''.join(filter_elems)
        if len(filter_elems) > 1:
            filter = '(&%s)' % filter

        if not filter:
            filter = '(objectClass=*)'

        try:
            res = conn.search(self.searchBase, self.searchScope, filter=filter,
                              attrs=[self.idAttribute])
        except NoSuchObject:
            return ()

        prefix = self.principalIdPrefix
        infos = []
        for dn, entry in res:
            try:
                infos.append(prefix+entry[self.idAttribute][0])
            except (KeyError, IndexError):
                pass

        if start is None:
            start = 0
        if batch_size is not None:
            return infos[start:start+batch_size]
        else:
            return infos[start:]
