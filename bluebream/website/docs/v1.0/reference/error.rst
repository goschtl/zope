.. _error:

Error References
================

Unauthorized
------------

**Unauthorized** is an exception which is caught by z3c.evalexception.  It
is difficult to decide whether the exception was raised because the user was
not authorized initially or because he has not enough permissions.  This
means you are not able to access a page where you have to be logged-in when
you start BlueBream using debug.ini.

This only happens for basic auth.

A solution could be:

- start with deploy.ini
- authorize using basic auth
- restart using debug.ini
