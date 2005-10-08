====================
XMLRPC Introspection
====================

This Zope 3 package provides an xmlrpcintrospection mechanism,
as defined here:

    http://xmlrpc-c.sourceforge.net/xmlrpc-howto/xmlrpc-howto-api-introspection.html

It registers three new xmlrpc methods:

    - `listMethods()`: Lists all xmlrpc methods (ie views) registered for the current object

    - `methodHelp(method_name)`: Returns the method documentation of the given method.

    - `methodSignature(method_name)`: Returns the method documentation of the given method.

It is based on introspection mechanisms provided by the apidoc package.