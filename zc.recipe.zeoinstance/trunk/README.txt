Recipe for creating a ZEO instance
======================================

This recipe creates a basic ZEO instance.

The recipe takes the following options:

zeo 
   The name of a section providing a ZEO installation location.  This
   defaults to zeo.  The section is required to have a location option
   giving the location of the installation.  This could be a section
   used to install a part, like a Zope 3 checkout, or simply a section
   with a location option pointing to an existing install. This
   location must have a mkzeoinstance script in it's bin directory.

database
   The name of a section defining a zconfig option that has a zodb
   section.

port
   The port to listen on. This defaults to 8100
      
The recipe generates a zconfig option that can be used by parts
needing a database configuration.

To do
-----

- This probably only works with a zope3-internal ZEO installation,
  because of the way we determine the location (and name?) of the
  mkzeoinstance script.

- Need tests

- Support for more configuration options.

- Instance generation using a recipe-internal template for zeo.conf,
  rather than hacking the configuration file produced by
  mkzeoinstance.


  
