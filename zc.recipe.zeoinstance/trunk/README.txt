Recipe for creating a ZEO instance
======================================

This recipe creates a Zope instance that has been extended by a
collection of eggs.

The recipe takes the following options:

zeo 
   The name of a section providing a Zope 3 installation definition.
   This defaults to zeo.  The section is required to have a 
   location option giving the location of the installation.  This
   could be a section used to install a part, like a Zope 3 checkout,
   or simply a section with a location option pointing to an existing
   install. 

database
   The name of a section defining a zconfig option that has a zodb
   section.

      
To do
-----

- Need tests

- Support for more configuration options.
