Overview
========

Dobbin is a relational database abstraction layer supporting a
semi-transparent object persistance model.

It relies on descriptive attribute and field declarations based on
zope.interface and zope.schema. Strong typing is supported (and
encouraged when possible), but not required.

Tables are created on-the-fly with 1:1 correspondence to interfaces
with no inheritance (base interface). As such, objects are modelled as
a join between the interfaces they implement.

Authors
-------

This package was designed and implemented by Malthe Borch, Stefan
Eletzhofer with parts contributed by Kapil Thangavelu and Laurence
Rowe. It's licensed as ZPL.

