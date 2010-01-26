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

Subscriber
~~~~~~~~~~

Handler
~~~~~~~


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

PasteScript
~~~~~~~~~~~

PasteDeploy
~~~~~~~~~~~

ZCML
~~~~

The Zope Configuration Markup Language (ZCML) is an XML based
configuration system for registration of components.  Instead of
using Python API for registration, you can use ZCML

