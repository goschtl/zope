=========
Mars View
=========

Introduction
------------

`Grok`_ is a project which seeks to provide convention over configuration.

``Martian`` grew from `Grok`_:

 Martian provides a framework that allows configuration to be expressed
 in declarative Python code. These declarations can often be deduced
 from the structure of the code itself. The idea is to make these
 declarations so minimal and easy to read that even extensive
 configuration does not overly burden the programmers working with the
 code. Configuration actions are executed during a separate phase
 ("grok time"), not at import time, which makes it easier to reason
 about and easier to test.

 The ``martian`` package is a spin-off from the `Grok`_ project, in the
 context of which this codebase was first developed. While Grok uses
 it, the code is completely independent of Grok.

.. _Grok: http://grok.zope.org/

Mars View
---------

The mars.view package provides the means of creating and configuring ``views``
for an application using Zope3.

These views use presentation patterns used by other z3c packages.
