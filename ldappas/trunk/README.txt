LDAP PAS Plugin
===============

This is a plugins for PAS to deal with LDAP. It depends on the
`ldapadapter` module (which itself depends on `python-ldap`).

Authentication and Search
-------------------------

This plugin allows one to authenticate and make searches. It is
configured with:

- LDAP adapter to use.

- The search base and scope.

- The attributes for principal login, id and title (which means you can
  have a login different than the id used by zope to represent the
  principal), for instance the login attribute can be 'cn' while the id
  attribute can be 'uid'.

- The prefix to add to the principal id (so that each authentication
  source can have a different namespace for its ids).
