Concepts
========

Interface
---------

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
---------------------------

The main idea in the Zope Component Architecture is the use of
components, rather than multiple-inheritence for managing complexity.

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
-----

Events are objects that represent something happening in a system.
They are used to extend processing by providing processing plug
points.

Adpater
-------

Adapter takes the Interface of an existing component and adapts it to
provide another Interface.

Utility
-------

Subscriber
----------

Handler
-------

ZCML
----

The Zope Configuration Markup Language (ZCML) is an XML based
configuration system for registration of components.  Instead of
using Python API for registration, you can use ZCML

WSGI
----

ZODB
----

Python based object database.

Object Publishing
-----------------

View
----

Browser Page
------------

Browser Resource
----------------

Container
---------

Content Object
--------------

Layer
-----

Skin
----

Annotation
----------

Content Provider
----------------

Viewlet
-------

Viewlets provide a generic framework for building pluggable user
interfaces.
