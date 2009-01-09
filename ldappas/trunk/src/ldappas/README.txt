==========================
LDAP Authentication Plugin
==========================

This is a plugin for the pluggable authentication utility (located at
``zope.app.authentication``) to deal with LDAP principal sources. It depends
on the ``ldapadapter`` module (which itself depends on `python-ldap`).

Authentication and Search
-------------------------

This plugin allows one to authenticate and make searches. It is configured
with:

- A LDAP adapter to use.

- The search base and scope.

- The attributes for principal login, id and title (which means you can
  have a login different than the id used by zope to represent the
  principal), for instance the login attribute can be `cn` while the id
  attribute can be `uid`.

- The prefix to add to the principal id (so that each authentication
  source can have a different namespace for its ids).

The authentication utility is located in

  >>> import ldappas.authentication

As mentioned before, we need a LDAP Adapter. To avoid needing to
connect to a real LDAP server for these tests, a fake LDAP adapter was
developed and has already been registered under the name
`fake_ldap_adapter`.

Now that the LDAP adapter is registered, we can instantiate the LDAP
authentication:

  >>> auth = ldappas.authentication.LDAPAuthentication()
  >>> auth.adapterName = 'fake_ldap_adapter'
  >>> auth.searchBase = 'dc=test'
  >>> auth.searchScope = 'sub'
  >>> auth.groupsSearchBase = 'ou=groups'
  >>> auth.groupsSearchScope = 'sub'
  >>> auth.loginAttribute = 'cn'
  >>> auth.principalIdPrefix = ''
  >>> auth.idAttribute = 'uid'
  >>> auth.titleAttribute = 'sn'
  >>> auth.groupsAttribute = 'ou'
  >>> auth.groupIdAttribute = 'cn'
  >>> da = auth.getLDAPAdapter()

The first task is to authenticate a set of credentials. Incorrect credentials
types are rejected.

  >>> auth.authenticateCredentials(123) is None
  True
  >>> auth.authenticateCredentials({'glop': 'bzz'}) is None
  True

You cannot authenticate if the search returns several results.

  >>> len(da.connect().search('dc=test', 'sub', '(cn=many)')) > 1
  True
  >>> auth.authenticateCredentials({'login': 'many', 'password': 'p'}) is None
  True

You cannot authenticate if the search returns nothing.

  >>> conn = da.connect()
  >>> len(conn.search('dc=test', 'sub', '(cn=none)')) == 0
  True
  >>> auth.authenticateCredentials({'login': 'none', 'password': 'p'}) is None
  True

You cannot authenticate with the wrong password.

  >>> auth.authenticateCredentials({'login': 'ok', 'password': 'hm'}) is None
  True

Authentication succeeds if you provide the correct password.

  >>> principal = auth.authenticateCredentials({'login': 'ok', 
  ...                                          'password': '42pw'})
  >>> principal, principal.login, principal.title, principal.description
  (PrincipalInfo(u'42'), u'ok', u'the question', u'the question')

The id returned comes from a configurable attribute, and can be prefixed so
that it is unique.

  >>> auth.principalIdPrefix = 'ldap.'
  >>> auth.idAttribute = 'cn'
  >>> auth.authenticateCredentials({'login': 'ok', 'password': '42pw'})
  PrincipalInfo(u'ldap.ok')

The id attribute `dn` can be specified to use the full dn as id.

  >>> auth.idAttribute = 'dn'
  >>> auth.authenticateCredentials({'login': 'ok', 'password': '42pw'})
  PrincipalInfo(u'ldap.uid=42,dc=test')

If the id attribute returns several values, the first one is used.

  >>> auth.idAttribute = 'mult'
  >>> conn.search('dc=test', 'sub', '(cn=ok)')[0][1]['mult']
  [u'm1', u'm2']
  >>> auth.authenticateCredentials({'login': 'ok', 'password': '42pw'})
  PrincipalInfo(u'ldap.m1')

Authentication fails if the id attribute is not present:

  >>> auth.idAttribute = 'nonesuch'
  >>> conn.search('dc=test', 'sub', '(cn=ok)')[0][1]['nonesuch']
  Traceback (most recent call last):
  ...
  KeyError: 'nonesuch'
  >>> auth.authenticateCredentials({'login': 'ok', 'password': '42pw'}) is None
  True

You cannot authenticate if the server to which the adapter connects is down.

  >>> da._isDown = True
  >>> auth.authenticateCredentials({'login': 'ok', 'password': '42pw'}) is None
  True
  >>> da._isDown = False

You cannot authenticate if the plugin has a bad configuration.

  >>> auth.searchBase = 'dc=bzzt'
  >>> auth.authenticateCredentials({'login': 'ok', 'password': '42pw'}) is None
  True

When dealing with security settings, only the prinipal id is stored. To
retrieve the principal object, the pluggable authetication utility uses the
authenticator's ``principalInfo(id)`` method to extract further details.

If the id is not in this plugin, return nothing.   

  >>> auth.idAttribute = 'uid'   
  >>> auth.searchBase = 'dc=test'
  >>> auth.principalInfo('42') is None   
  True

Otherwise return the info if we have it.   

  >>> auth.principalInfo('ldap.123') is None   
  True   
  >>> info = auth.principalInfo('ldap.42')   
  >>> info, info.login, info.title, info.description
  (PrincipalInfo('ldap.42'), u'ok', u'the question', u'the question')

If the principal we want information for is actually a group, we will
also get info:

  >>> info = auth.principalInfo('ldap.mygroup')
  >>> info.id
  'ldap.mygroup'

Although the group exists, we cannot authenticate with it directly:

  >>> auth.authenticateCredentials({'login': 'mygroup', 
  ...                               'password': 'something'}) is None
  True

In user interfaces, you commonly want to search through the available
principals for management purposes. The authentication plugin provides
an API for searching through the principals. An empty search returns
everything, except groups.

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


If any of the groupsSearchBase, groupsSearchScope or groupIdAttribute
are not set (they're not required), we can still get principalInfo:

  >>> auth.groupsSearchBase = ''
  >>> auth.idAttribute = 'uid'   
  >>> auth.searchBase = 'dc=test'
  >>> auth.principalInfo('ldap.44') is None   
  True

  >>> auth.groupsSearchBase = 'ou=groups'
  >>> auth.groupsSearchScope = ''
  >>> auth.principalInfo('ldap.44') is None   
  True

  >>> auth.groupsSearchScope = 'sub'
  >>> auth.groupIdAttribute = ''
  >>> auth.principalInfo('ldap.44') is None   
  True

Integration with the Pluggable Authentication Utility
-----------------------------------------------------

Now that we have seen how the LDAP authentication plugin behaves autonomously,
let's have a brief look on how the plugin behaves inside the authentication
utility. The first step is to register the LDAP authentication plugin as an
authenticator utility:

  >>> from zope.component import provideUtility
  >>> from zope.app.authentication.interfaces import IAuthenticatorPlugin
  >>> provideUtility(auth, provides=IAuthenticatorPlugin,
  ...                name='ldap-authenticator')

We also need a credentials plugin that will extract the credentials from the
request:

  >>> import zope.interface
  >>> from zope.app.authentication.interfaces import ICredentialsPlugin

  >>> class MyCredentialsPlugin:
  ...
  ...     zope.interface.implements(ICredentialsPlugin)
  ...
  ...     def extractCredentials(self, request):
  ...         return request.get('credentials')
  ...
  ...     def challenge(self, request):
  ...         pass # challenge is a no-op for this plugin
  ...
  ...     def logout(request):
  ...         pass # logout is a no-op for this plugin

  >>> provideUtility(MyCredentialsPlugin(), name='simple-creds')

Now, as we have seen the authenticator is only responsible for providing
principal information, but not to generate the principals itself. Thus we have
to register an adapter that can create principals from principal infos:

  >>> from zope.component import provideAdapter
  >>> from zope.app.authentication import principalfolder
  >>> provideAdapter(principalfolder.AuthenticatedPrincipalFactory)

We are finally ready to create a pluggable authentication utility and register
the two plugins with it:

  >>> from zope.app import authentication
  >>> pau = authentication.PluggableAuthentication('pau.')
  >>> pau.credentialsPlugins = ('simple-creds', )
  >>> pau.authenticatorPlugins = ('ldap-authenticator', )

And now we can just authenticate a user using LDAP:

  >>> auth.idAttribute = 'cn'
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest(credentials={'login': 'ok', 'password': '42pw'})
  >>> principal = pau.authenticate(request)
  >>> principal
  Principal(u'pau.ldap.ok')

You can also ask the authentication utility about a particular principal, once
you have its id:

  >>> provideAdapter(principalfolder.FoundPrincipalFactory)

  >>> pau.getPrincipal(u'pau.ldap.ok')
  Principal(u'pau.ldap.ok')
