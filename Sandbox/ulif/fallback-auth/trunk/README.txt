****************
z3c.fallbackauth
****************

Provides an ``AuthenticatorPlugin`` for use with the Zope 3 Pluggable
Authentication Utility (PAU). The plugin authenticates against
principals (users) of the Zope principal registry, which normally is
created at startup. Such it is able to serve as a fallback solution,
when other authenticator plugins fail and default (Basic Auth)
authentication is disabled.

Please refer to README.txt in src/z3c/fallbackauth for more
information. 
