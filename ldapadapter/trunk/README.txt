===========
LDAPAdapter 
===========

The LDAPAdapter provides a mechanism for to connect to a LDAP server.

LDAPAdapter
===========

The primary job of an ldap adapter is to store the settings of
a LDAP server connection.

Let's look at an example:

  >>> from ldapadapter.interfaces import ILDAPAdapter
  >>> from ldapadapter.interfaces import ILDAPConnection
  >>> from ldapadapter import LDAPAdapter

  >>> host = u'localhost'
  >>> port = 389
  >>> useSSL = False
  >>> da = LDAPAdapter(host, port)
  >>> (da.host, da.port, da.useSSL)
  (u'localhost', 389, False)

  >>> dn = 'Manager'
  >>> pw = ''
  >>> conn = da.connect(dn, pw)

  >>> conn.add('cn=yo,o=test,dc=org', {'cn': ['yo']})

The fake implementation of ldap used for the tests returns a simpler
result than a real server would:

  >>> conn.search('o=test,dc=org', 'sub')
  [(u'cn=yo', {'cn': [u'yo']})]

