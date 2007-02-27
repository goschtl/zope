Recipe for createing a Zope 3 instance
======================================

This recipe creates a Zope instance that has been extended by a
collection of eggs.

The recipe takes the following options:

zope3 
   The name of a section providing a Zope 3 installation definition.
   This defaults to zope3.  The section is required to have a 
   location option giving the location of the installation.  This
   could be a section used to install a part, like a Zope 3 checkout,
   or simply a section with a location option pointing to an existing
   install. 

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
