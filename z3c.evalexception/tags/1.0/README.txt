``paste.evalexception`` lets you interactively debug exceptions in
your WSGI app.  ``z3c.evalexception`` is a small wrapper around that
so that it works with the stock Zope 3 application server.

Here's a simple PasteDeploy configuration file that sets up the Zope 3
application server on top of the WSGIUtils HTTP server with the
``z3c.evalexception`` middleware::

  [filter-app:main]
  use = egg:z3c.evalexception
  next = zope

  [app:zope]
  use = egg:zope.paste
  site_definition = parts/app/site.zcml
  file_storage = parts/data/Data.fs

  [server:main]
  use = egg:PasteScript#wsgiutils
  host = 127.0.0.1
  port = 8080
