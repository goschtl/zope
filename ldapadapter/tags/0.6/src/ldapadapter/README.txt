===========
LDAPAdapter
===========

The LDAPAdapter provides a mechanism to connect to an LDAP server and
send commands to it.

LDAPAdapter
===========

An LDAP adapter stores the settings to use to connect to an LDAP server.
You get an LDAP adapter by calling LDAPAdapter, which implements
ILDAPAdapter:

  >>> from ldapadapter.utility import LDAPAdapter
  >>> from ldapadapter.interfaces import ILDAPAdapter
  >>> from zope.interface.verify import verifyClass, verifyObject
  >>> verifyClass(ILDAPAdapter, LDAPAdapter)
  True

The adapter is set up by giving it a host name and a port.

  >>> da = LDAPAdapter('localhost', 389)
  >>> verifyObject(ILDAPAdapter, da)
  True
  >>> (da.host, da.port, da.useSSL)
  ('localhost', 389, False)

If you want, you can request an SSL connection:

  >>> da = LDAPAdapter('localhost', 389, useSSL=True)
  >>> (da.host, da.port, da.useSSL)
  ('localhost', 389, True)

You can also provide a default bind DN and password to use by default
for future connections:

  >>> da = LDAPAdapter('localhost', 389,
  ...                  bindDN='cn=Manager', bindPassword='secret')
  >>> (da.host, da.port, da.bindDN)
  ('localhost', 389, 'cn=Manager')

LDAPConnection
==============

Once you have an LDAP adapter, you can get an LDAP connection by calling
connect() on the database adapter.

If the server doesn't answer, you'll get an exception when you connect:

  >>> LDAPAdapter('down', 389).connect('', '')
  Traceback (most recent call last):
  ...
  ServerDown

You can either use the default bind DN and password if these have been
specified in the adapter:

  >>> conn = da.connect()

Or you can provide specific binding parameters:

  >>> conn = da.connect('cn=Manager,dc=org', 'supersecret')

If you provide an incorrect password, an exception is returned:

  >>> conn = da.connect('cn=Bob', 'pretend')
  Traceback (most recent call last):
  ...
  InvalidCredentials

You can bind anonymously by using an empty DN and password:

  >>> conn = da.connect('', '')

The connection object that is returned implements ILDAPConnection:

  >>> from ldapadapter.interfaces import ILDAPConnection
  >>> verifyObject(ILDAPConnection, conn)
  True


Commands
========

Once you have an LDAP connection, you can start sending commands using
it. (The fake implementation of the ldap module used for the tests
returns simpler results than a real server would.)

Add
---

Let's add a few simple entries.

  >>> conn.add('dc=test', {'dc': ['test']})
  >>> conn.add('cn=foo,dc=test', {'cn': ['foo'], 'givenName': ['John']})
  >>> conn.add('cn=bar,dc=test', {'cn': ['bar'], 'givenName': ['Joey']})
  >>> conn.add('cn=baz,dc=test', {'cn': ['baz'], 'givenName': ['Raoul']})

Search
------

Let's now search for entries. The scope argument controls what kind of
search is done. You can choose to return a subset of the attributes.

  >>> conn.search('dc=test', scope='base')
  [(u'dc=test', {'dc': [u'test']})]

  >>> res = conn.search('dc=test', scope='one', attrs=['cn'])
  >>> pprint(res)
  [(u'cn=foo,dc=test', {'cn': [u'foo']}),
   (u'cn=bar,dc=test', {'cn': [u'bar']}),
   (u'cn=baz,dc=test', {'cn': [u'baz']})]

The default scope is 'sub':

  >>> res = conn.search('dc=test', attrs=['givenName'])
  >>> pprint(res)
  [(u'cn=foo,dc=test', {'givenName': [u'John']}),
   (u'cn=bar,dc=test', {'givenName': [u'Joey']}),
   (u'dc=test', {}),
   (u'cn=baz,dc=test', {'givenName': [u'Raoul']})]

You can use a search filter to filter the entries returned:

  >>> res = conn.search('dc=test', scope='sub', filter='(cn=ba*)',
  ...                   attrs=['cn'])
  >>> pprint(res)
  [(u'cn=bar,dc=test', {'cn': [u'bar']}),
   (u'cn=baz,dc=test', {'cn': [u'baz']})]

Searching on an base that doesn't exist returns an exception:

  >>> conn.search('dc=bzzt')
  Traceback (most recent call last):
  ...
  NoSuchObject: dc=bzzt

Modify
------

When modifying an entry, you pass new values for some attributes:

  >>> conn.modify('cn=foo,dc=test', {'givenName': ['Pete']})
  >>> conn.search('cn=foo,dc=test', attrs=['givenName'])
  [(u'cn=foo,dc=test', {'givenName': [u'Pete']})]

  >>> conn.modify('cn=foo,dc=test', {'givenName': ['Bob', 'Robert']})
  >>> conn.search('cn=foo,dc=test', attrs=['givenName'])
  [(u'cn=foo,dc=test', {'givenName': [u'Bob', u'Robert']})]

Passing an empty value for an attribute remove it from the entry:

  >>> conn.modify('cn=foo,dc=test', {'givenName': []})
  >>> conn.search('cn=foo,dc=test')
  [(u'cn=foo,dc=test', {'cn': [u'foo']})]

Delete
------

You can delete an entry.

  >>> conn.delete('cn=foo,dc=test')
  >>> conn.search('cn=foo,dc=test')
  Traceback (most recent call last):
  ...
  NoSuchObject: cn=foo,dc=test


Checking the Connection
=======================

When first configuring a LDAP adapter, we often want to check the success of
connecting to the LDAP server. This can be done with a check adapter:

  >>> from ldapadapter import check
  >>> check = check.CheckLDAPAdapter(da)

This adapter has a ``testConnection()`` method that accepts a `bindDN` and
`bindPassword` argument to establish the conection:

  >>> check.testConnection('cn=Manager,dc=org', 'supersecret') \
  ... # doctest: +ELLIPSIS
  ['... start check connection', 
   '... try connect with:', 
   '... serverURL = ldap://localhost:389', 
   '... bindDN = cn=Manager,dc=org', 
   '... <strong>connection OK!</strong>', 
   '... <strong><ldapadapter.utility.LDAPConnection object at ...></strong>']

  >>> check.testConnection('cn=Bob', 'pretend')
  ['... start check connection', 
   '... try connect with:', 
   '... serverURL = ldap://localhost:389', 
   '... bindDN = cn=Bob', '... <strong>Test failed!</strong>']
