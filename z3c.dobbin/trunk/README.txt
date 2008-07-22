Overview
========

Dobbin is an object database implemented on top of SQLAlchemy. It's
designed to mimick the behavior of the Zope object database (ZODB)
while providing greater flexibility and control of the storage.

It supports strong typing with native SQL columns by utilizing the
declarative field definitions from zope.schema. Weak typing is
supported using the Python pickle protocol. Attributes are
automatically persisted with the exception of those starting with the
characters "_v_" (volatile attributes).

Tables to support the strongly typed attributes are created on-the-fly
with a 1:1 correspondence to interfaces with no inheritance (base
interface). As such, objects are modelled as a join between the
interfaces they implement plus a table that maintains object metadata
and weakly typed instance attributes.

Authors
-------

This package was designed and implemented by Malthe Borch and Stefan
Eletzhofer with parts contributed by Kapil Thangavelu and Laurence
Rowe. It's licensed as ZPL.

