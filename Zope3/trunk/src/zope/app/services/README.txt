==============
Local Services
==============

:Author: Jim Fulton
:Version: $Revision: 1.9 $

This package includes implementations of several local services.
It also contains infrastructure for implementing local services.

Implementing local services is not too difficult, but there can be a
lot of details that are hard to remember.

A service is a component that implements a specific interface *and*
that has the responsibility to collaborate with services above it.
Local services are stored in the Zope object database, so they also
need to be persistent.  Finally, many local services support modular
registration through registration objects.

A few words on the difference between local and global services:

- Local services (usually) exist in the ZODB; global services don't.

- Local services apply to a specific part of the object hierarchy;
  global services (as their name suggests) don't.

- Local services are (usually) created and configured through the ZMI;
  global services are created and configured by ZCML directives.

- Local services are expected to collaborate with services "above"
  them in the object hierarchy, or with the global service; global
  services by definition have nothing "above" them.

  (Note that it's up to the service to decide what form the
  collaboration will take.  An acceptable form of collaboration is to
  not collaborate at all.

Registration
------------

Many services act as component registries.  Their primary job is to
allow components to be looked up based on parameters such as names,
interfaces or both. Examples of component registries include the
adapter service, the view service, the service service, and the
utility service.

An important feature of component registration services is that they
support multiple conflicting registrations for the same registration
parameters.  At most one of the conflicting registrations is active.
A site developer can switch between alternate components by simply
changing which one is active.

Consider the following scenario.  A product provides a utility.  A
site manager gets a new version of the utility and installs
it.  The new version is active.  The site developer then finds a
bug in the new version.  Because the old utility is still registered,
the site developer can easily switch back to it by making it active.
In fact, the site manager only needs to inactivate the new version and
the old version becomes active again.

To support this registration flexibility, Zope provides a registration
framework:

- Registration objects manage registration parameters and other data.
  They also provide access to registered components. In some cases,
  such as adapters and views, they are responsible for constructing
  components on the fly.

- Registration managers support management of registration objects
  in folders.  Each folder has a registration manager containing all
  of the registration objects for that folder.

- RegistrationStack objects manage multiple registrations for
  the same registration parameters (at most one of which is active at
  any given time).  For example, in the case of a utility service
  these would be registrations for the same interface and name.

There are two kinds of registrations:

- Local-object registrations register objects in site-management
  folders, such as service instances, utility instances, database
  connections, caches, and templates.  

  Local objects are named using a path.

  Local-object registrations are primarily managed through the objects
  that they register. The objects have a "Registrations" tab that
  allows the registrations (usually 1) for the objects to be managed.

  Local-object registrations can also be browsed and edited in the
  registration manager for the folder containing the registered
  components. 

- Module-global registrations register objects stored in
  modules. Objects in modules aren't managable directly, so we can't
  manage their registrations through them.  (The state of an object
  stored in a module must be represented solely by the module source.)
  
  Module-global objects are named using dotted names.

  Module-global registrations are added, browsed and edited in
  registration mananagers.  

Implementation of services that support registration is substantially
more difficult that implementation of non-registry services.

Examples
--------

Implementation of local services is described through examples.

- The error reporting service is among the simplest examples because
  error reporting services don't support registration and don't
  delegate requests to services above.

  See error.txt

- The utility service is an example of a service that supports
  local-object registration. It also provides a simple example of a
  service that delegates to services above it.

  See utility.txt.
