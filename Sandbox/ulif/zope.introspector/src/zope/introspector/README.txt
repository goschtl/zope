zope.introspector
**********************

:Test-Layer: unit

The `zope.introspector` package provides an extensible framework
for retrieving 'data' on 'entities'. It makes use of
grokcore.component for registration of adapters and utilities.

'Entity' in that respect means everything, that is descriptable by a
name in Python or everything, that can be passed to a method. In other
words: if you can pass something to a callable, then the introspector
should be able to give you some information about it.

'Data' in that respect means a container containing a set of data,
describing the given entity. The container might contain primitive
values (like numbers or strings) as well as more complex objects,
callables etc.

In plain words: Given a certain object you get a dataset describing
it.

Support for modification of objects (for instance for debugging
purposes) is still not implemented. This package also does not include
viewing components to display the results.


Inspecting Objects
===================

Because many objects have many different aspects that can be examined,
we provide a set of 'examiners', each one responsible for a certain
aspect.

Currently, the following introspectors are available

* ``ObjectInfo`` and relatives

  Gives you information about simple and built-in types like strings,
  classes, packages and functions. See `objectinfo.txt` to learn more
  about that.

* ``UtilityInfo`` and relatives

  Gives you information about the utilities that are available for a
  certain objects. See `utilityinfo.txt` to learn more about that.


Writing your own introspector
=============================

XXX To come
