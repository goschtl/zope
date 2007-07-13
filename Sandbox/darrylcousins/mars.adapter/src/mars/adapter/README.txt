============
Mars Adapter
============

Introduction
------------

`Grok`_ is a project which seeks to provide convention over configuration.

``Martian`` grew from `Grok`_:

Martian is a library that allows the embedding of configuration information in
Python code. Martian can then grok the system and do the appropriate
configuration registrations.

.. _Grok: http://grok.zope.org/

Mars Adapter
------------

The mars.adapter package provides the means of creating and configuring simple
``adapters`` for an application using Zope3.

Example Code
------------

::

 class DefaultDate(mars.adapter.AdapterFactory):
     grok.name('default')
     mars.adapter.factory(z3c.form.widget.ComputedWidgetAttribute(
                         lambda adapter: datetime.date.today(),
                         field=IHelloWorld['when'], view=IAddForm))


Directives specific to this package
-----------------------------------

* mars.adapter.factory(factory):
  The factory to be registered
  **Required**

Relevant grok directives
------------------------

* grok.name(name):
  If defined the factory will be registered as a `named adapter`.
  Default: empty string


Tests
-----

See test directory.


