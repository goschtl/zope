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

Event
-----

Events are objects that represent something happening in a system.
They are used to extend processing by providing processing plug
points.

Adpater
-------


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
