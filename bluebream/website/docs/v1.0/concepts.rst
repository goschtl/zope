Concepts and Technologies
=========================

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

Concepts
--------

Interface
~~~~~~~~~

Interfaces are objects that specify (document) the external behavior
of objects that "provide" them.  An interface specifies behavior
through:

- Informal documentation in a doc string

- Attribute definitions

- Invariants, which are conditions that must hold for objects that
  provide the interface

Some of the motivations for using interfaces are:

- Avoid monolithic design by developing small, exchangeable pieces

- Model external responsibility, functionality, and behavior

- Establish contracts between pieces of functionality

- Document the API

Zope Component Architecture
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main idea in the Zope Component Architecture is the use of
components, rather than multiple-inheritance for managing complexity.

Zope Component Architecture is about how to create reusable
components, but not reusable components itself.

A component is a reusable object with introspectable interfaces.
Also components are cohesive and decoupled objects.  A component
provides an interface implemented in a class.  It doesn't matter how
a component is implemented, the important part is that it complies
with its interface contracts.  An interface is an object that
describes how you work with a particular component.  Using Zope
component architecture we can spread the complexity of systems over
multiple cooperating components.  Zope component architecture help us
to create two basic kinds of components, adapters and utilities.

Event
~~~~~

Events are objects that represent something happening in a system.
They are used to extend processing by providing processing plug
points.  The `zope.event <http://pypi.python.org/pypi/zope.event>`_
provides the basic event publishing system.  The ``zope.event``
package also provides a very simple event-dispatching system on which
more sophisticated event dispatching systems can be built.  For
example, a type-based event dispatching system that builds on
``zope.event`` can be found in zope.component.

Adapter
~~~~~~~

.. based on zope-cookbook.org

Summary: Adapter takes the Interface of an existing component and
adapts it to provide another Interface.

When applications gets bigger, there is a side effect on the code,
called the spaggethi effect: interactions between classes can lead to
unwanted dependencies and the code turns into a monolithic bloc.

Adapters provides a way to prevent from this, by implementing the
Liskov substitution principle.

Adapters provide a cooperation mechanism between any given object and
a particular context, using interfaces.  They allow an abritary type
of class to be compatible with a given interface, by giving a
compatibility layer.

This mechanism is used in systems like Microsoft COM's QueryAdapter,
and let the developer gathers objects in a speciﬁc functional
context.  This also known as glue code.

Adapters provides several advantages:

* They can gather class instances in contexts they where not
  implemented for, without having to change their code or make them
  depend on each other.

* They offer a smooth way to gather generic features, that can be
  applied on several kind of classes.

Adapters can be seen as a formalized duck typing and where proposed
some years ago in PEP 246.  There are also Python implementations of
it, like PyProtocols.

Utility
~~~~~~~

Utility components are components that serve only one specific
function, and are not designed to act on another component.  A good
analogy for Python programmers are functions and methods.  Utility
components, like Python functions, are standalone objects that do not
need any other objects to do their work.  Adapter components, like
Python methods, require another object to work upon.

Utility components will mostly be used for simple, throw-away
components that serve one simple task, like an XML parser.  Sometimes
it would be useful to register an object which is not adapting
anything.  Database connection, XML parser, object returning unique
Ids etc. are examples of these kinds of objects.  These kind of
components provided by the ZCA are called utility components.

Utilities are just objects that provide an interface and that are
looked up by an interface and a name.  This approach creates a global
registry by which instances can be registered and accessed by
different parts of your application, with no need to pass the
instances around as parameters.

Subscriber
~~~~~~~~~~

Handler
~~~~~~~

Component Registry
~~~~~~~~~~~~~~~~~~

Registries keep the list of which components are available, which
interface they provide, which interface(s) they possibly adapt, along
with an optional registration name.  The ``zope.component`` package
implements a global component registry.

Object Publishing
~~~~~~~~~~~~~~~~~

BlueBream puts your objects on the web.  This is called object
publishing.  One of BlueBream's unique characteristics is the way it
allows you to walk up to your objects and call methods on them with
simple URLs.  In addition to HTTP, BlueBream makes your objects
available to other network protocols including FTP, WebDAV and
XML-RPC.

View
~~~~

Browser Page
~~~~~~~~~~~~

Browser Resource
~~~~~~~~~~~~~~~~

Container
~~~~~~~~~

Content Object
~~~~~~~~~~~~~~

Layer
~~~~~

Skin
~~~~

Annotation
~~~~~~~~~~

Content Provider
~~~~~~~~~~~~~~~~

Viewlet
~~~~~~~

Viewlets provide a generic framework for building pluggable user
interfaces.

Technologies
------------

ZODB
~~~~

The Zope Object Database provides an object-oriented database for
Python that provides a high-degree of transparency.  Applications can
take advantage of object database features with few, if any, changes
to application logic.  ZODB includes features such as a pluggable
storage interface, rich transaction support, and undo.

WSGI
~~~~

:term:`WSGI` is the Web Server Gateway Interface.  It is a
specification for web servers and application servers to communicate
with web applications (though it can also be used for more than
that).  It is a Python standard, described in detail in `PEP 333
<http://www.python.org/dev/peps/pep-0333/>`_.

PasteScript
~~~~~~~~~~~

PasteScript is an external package created by Ian Bicking.

PasteScript is a framework for defining commands.  It comes with a
few commands out of the box, like ``paster serve`` and ``paster
create``.

The ``paster serve`` command loads and serves a WSGI application
defined in a Paste Deploy config file.  The ``paster create`` command
creates directory layout for packages from a template.

PasteDeploy
~~~~~~~~~~~

PasteDeploy is an external package created by Ian Bicking.  

PasteDeploy is a system for loading and configuring WSGI applications
and servers.  PasteDeploy create a WSGI app as specified in the
configuration file.  The INI format of configuration file is
specified by PasteDeploy.

From the PasteDeploy site:

Paste Deployment is a system for finding and configuring WSGI
applications and servers.  For WSGI application consumers it provides
a single, simple function (loadapp) for loading a WSGI application
from a configuration file or a Python Egg.  For WSGI application
providers it only asks for a single, simple entry point to your
application, so that application users don’t need to be exposed to
the implementation details of your application.

ZCML
~~~~

The Zope Configuration Markup Language (ZCML) is an XML based
configuration system for registration of components.  Instead of
using Python API for registration, you can use ZCML.  Security
declarations is also done in ZCML.

