Object Hub
==========

This package used to hold the object hub service. The object hub
service was responsible for:

- Managing short ids for objects, useful for indexing

- Keeping track of object locations.  This was important when the
  object hub was created, because it wasn't practical to use direct
  object references. No it is, so hub ids are no-longer useful for
  implementing location-independent object references.

The object hub service is dead.

In the future, there will be a utility for use by indexes, that
maintains short ids for objects. Perhaps this will be an indexing id
service.
