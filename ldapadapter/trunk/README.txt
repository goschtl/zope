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
