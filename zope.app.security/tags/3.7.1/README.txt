This package provides ZMI browser views for Zope security components.

It used to provide a large part of security functionality for Zope 3, but it was
factored out from this package to several little packages to reduce dependencies
and improve reusability.

The functionality was splitted into these new packages:

 * zope.authentication - the IAuthentication interface and related utilities.
 * zope.principalregistry - the global principal registry and its zcml directives.
 * zope.app.localpermission - the LocalPermission class that implements
   persistent permissions.

The rest of functionality that were provided by this package is merged into
``zope.security`` and ``zope.publisher``.

Backward-compatibility imports are provided to ensure that older applications
work. See CHANGES.txt for more info.
