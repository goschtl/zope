.. _error:

Error References
================

Unauthorized
------------

**Unauthorized** is an exception which is caught by z3c.evalexception.  It
is difficult to decide whether the exception was raised because the user was
not authorized initially or because he has not enough permissions.

This only happens for basic auth.

A solution could be:

- start with deploy.ini
- authorized using basic auth
- restart using debug.ini
