Introduction
============

z3c.persistentfactory provides a Persistentfactory class that wraps a
method in a persistent wrapper.  It also provides a function decorator
for use on class method definitions such that a persistent factory
will be used when the method is accessed on instance of the class.
See z3c/persistentfactory/README.txt for more details.

Also see z3c/persistentfactory/declarartions.txt for details about a
mixin Declarer class for classes implementing callable instances whose
declarations should pickle and persist correctly.


