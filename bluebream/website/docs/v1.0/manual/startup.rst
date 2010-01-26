Startup
=======

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

Introduction
------------

The web application created using BlueBream is a WSGI application.
The factory function which return the WSGI application object is
defined inside ``startup.py``.  For example, in the "ticket
collector" tutorial, you can see the factory function defined in
``src/tc/main/startup.py`` file::

  import zope.app.wsgi

  def application_factory(global_conf):
      zope_conf = global_conf['zope_conf']
      return zope.app.wsgi.getWSGIApplication(zope_conf)

BlueBream use PaseDeploy together with PasteScript to run the WSGI
application.  However, any :term:`WSGI` server can be used to run
BlueBream application [#wsgi_server]_.  PaseDeploy identify the WSGI
application factory from the entry point defined in the main package.
For example, in the "ticket collector" tutorial, you can see the
entry point defined in ``setup.py`` file::

      [paste.app_factory]
      main = tc.main.startup:application_factory

To load the WSGI application, you can use the ``paster serve``
command provided by PasteScript which expects an INI file as the
argument.  The INI file define WSGI application in a particular
format specified by PasteScript.  For example, in the "ticket
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
