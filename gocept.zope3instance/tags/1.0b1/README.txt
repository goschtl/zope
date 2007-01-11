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

user
   The user name and password for manager user

eggs
   One or more requirements for distributions to be included.

zcml

   If specified, provides the list of package ZCML files to include in
   the instance's package includes and their order.

   By default, the ZCML files normally included in package-includes
   are ommitted.  To includes these, include '*' in the list of
   includes.

   Each entry is a package name with an optional include type and file
   name.  An package name can be optionally followed by a ':' and a
   file name within the package.  The default file name is
   configure.zcml.  The string '-meta' can be included between the
   file name and the package name. If so, then the default file name
   is meta.zcml and the include will be treated as a meta include.
   Similarly for '-overrides'. For example, the include::

      foo.bar

   Causes the file named NNN-foo.bar-configure.zcml to be inserted
   into package-includes containing:

      <include package="foo.bar" file="configure.zcml" />

   where NNN is a 3-digit number computed from the order if the entry
   in the zcml option.

   The include:

      foo.bar-meta

   Causes the file named NNN-foo.bar-meta.zcml to be inserted
   into package-includes containing:

      <include package="foo.bar" file="meta.zcml" />

   The include:

      foo.bar-overrides:x.zcml

   Causes the file named NNN-foo.bar-overrides.zcml to be inserted
   into package-includes containing:

      <include package="foo.bar" file="x.zcml" />

      
To do
-----

- Need tests

- Hopefully, for Zope 3.4, we'll be able to make the instance-creation
  process more modular, which will allow a cleaner implementation for
  this recipe.

- Support for multiple storages

- Support for more configuration options.
