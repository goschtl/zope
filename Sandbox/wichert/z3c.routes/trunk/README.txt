Introduction
============

z3c.routes tries to bring routes_ to Zope, allowing you to use a mixture
of Zope traversal and routes for publication traversal.

Zope will normally use traversal to determine which object to publish.
z3c.routes makes it possible to assign a ``mapper`` to an object. The
routes inside the mapper will be used to find an object to publish. 

Usage
-----

Register an IRouteRoot adapter for an object which returns the routes
for that object. This will trigger a custom traverser which will try
to find a matching route when doing traversal.


Conceptual differences
----------------------

controllers and actions
~~~~~~~~~~~~~~~~~~~~~~~
Routes is heavily based around the concepts of ``controllers`` objects which
have ``action`` methods. Zope 3 works somewhat differently: it uses objects
for which different views are registered. This is reflected in how routes
are used.

Instead of calling an ``action`` method on a ``controller``, optionally with
some named parameters z3c.routes instantiates a ``content item``, optionally
with some named parameters``, and finds a view for it.

global vs local mappers
~~~~~~~~~~~~~~~~~~~~~~~
Most web framework using an application which has a single global mapper
instance which is used for all queries. In z3c.routes we start routing
at an object instead of the application root, and accordingly each object
can have its own mapper.

.. _routes: http://routes.groovie.org/

