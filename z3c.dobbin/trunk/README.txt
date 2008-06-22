Overview
========

Dobbin is a relational database abstraction layer supporting a
semi-transparent object persistance model.

It relies on descriptive attribute and field declarations based on
zope.interface and zope.schema.

Tables are created automatically with a 1:1 correspondence to an
interface with no inheritance (minimal interface). As such, objects
are modelled as a join between the interfaces it implements.

Authors
-------

This package was designed and implemented by Malthe Borch, Stefan
Eletzhofer. It's licensed as ZPL.

