.. _man-startup:

Startup
=======

Introduction
------------

The BlueBream framework creates WSGI applications, which can run
behind any WSGI compliant web servers.  The main application is
configured and created via a factory function defined inside
``startup.py``.  This functions returns the WSGI complaint
application object to the server.  For example, in the "ticket
collector" tutorial, you can see the factory function defined in
``src/tc/main/startup.py`` file::

  import zope.app.wsgi

  def application_factory(global_conf):
      zope_conf = global_conf['zope_conf']
      return zope.app.wsgi.getWSGIApplication(zope_conf)

PaseDeploy together with PasteScript are then used to run the WSGI
application.  However, any :term:`WSGI` server can be used to run
BlueBream application [#wsgi_server]_.  We provide PaseDeploy with
the WSGI application factory as an entry point.  For example, in the
"ticket collector" tutorial, you can see the entry point defined in
``setup.py`` file::

      [paste.app_factory]
      main = tc.main.startup:application_factory

The application can now be launched as a web service using the 
``paster serve`` command provided by PasteScript.  To configure the
web server, an INI file has to be passed to the command as an argument.
The INI file defines the WSGI application, any WSGI middleware we may
want and web server options.  For example, in the "ticket
collector" tutorial, you can see the WSGI application defined in
``deploy.ini`` file::

  [app:main]
  use = egg:ticketcollector

  [server:main]
  use = egg:Paste#http
  host = 127.0.0.1
  port = 8080

  [DEFAULT]
  # set the name of the zope.conf file
  zope_conf = %(here)s/etc/zope.conf

You can read more about PasteDeploy and PasteScript in the
PythonPaste site.

Running WSGI application
------------------------

When you run BlueBream application using the ``paster server``
command, you can see something like this::

  $ ./bin/paster serve deploy.ini
  ...
  Starting server in PID 13367.
  serving on http://127.0.0.1:8080

.. [#wsgi_server] WSGI servers like :term:`mod_wsgi` don't
   require the ``paster serve`` command provided by
   :term:`PasteDeploy` to run the WSGI server.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
