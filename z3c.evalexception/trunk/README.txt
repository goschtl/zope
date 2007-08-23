``z3c.evalexception`` provides two WSGI middlewares for debugging web
applications running on the ``zope.publisher`` object publishing
framework (e.g. Zope 3).  Both middlewares will intercept an exception
thrown by the application and provide means for debugging.

Interactive AJAX debugger
=========================

``z3c.evalexception.ZopeEvalException`` lets you interactively debug
exceptions from a browser.  It is a small wrapper around the
``EvalException`` middleware from ``paste.evalexception``.  You can
easily refer to it in a PasteDeploy-style configuration file using the
``ajax`` entry-point::

  [filter-app:main]
  use = egg:z3c.evalexception#ajax
  next = zope

  [app:zope]
  use = egg:YourApp

  [server:main]
  use = egg:Paste#http
  host = 127.0.0.1
  port = 8080

Post-mortem pdb
===============

``z3c.evalexception.PostMortemDebug`` invokes pdb's post-mortem mode
when the application has thrown an exception.  You can refer to it in
a PasteDeploy-style configuration file using the ``pdb`` entry-point::

  [filter-app:main]
  use = egg:z3c.evalexception#pdb
  next = zope

  [app:zope]
  use = egg:YourApp

  [server:main]
  use = egg:Paste#http
  host = 127.0.0.1
  port = 8080

Changes
=======

2.0 (2007-08-23)
----------------

Added the ``PostMortemDebug`` (pdb) middelware.

1.0 (2007-06-02)
----------------

Initial release, featuring the Zope 3-compatible interactive AJAX
debugger from Paste.
