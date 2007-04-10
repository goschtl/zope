Recipe for createing a Zope 3 instance
======================================

This recipe creates a Zope instance that has been extended by a
collection of eggs.

A Zope installation or checkout is not required by this recipe. You should
make your application depend on zope.app.

The recipe takes the following options:

database
   The name of a section defining a zconfig option that has a zodb
   section.

admin-user
   The user name for the manager user.

admin-password
   The password for the manager user.

eggs
   One or more requirements for distributions to be included.


To do
-----

- Need tests

- Hopefully, for Zope 3.4, we'll be able to make the instance-creation
  process more modular, which will allow a cleaner implementation for
  this recipe.

- Support for multiple storages

- Support for more configuration options.
