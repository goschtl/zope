With ``zopeproject`` you can start a new Zope-based web application from
scratch with just a two commands::

  $ easy_install zopeproject
  $ zopeproject MyZopeProj

This will ask you the name and password for an initial administrator
user.  It will also ask you where to put the Python packages ("eggs")
that it downloads.  This way multiple projects created with
``zopeproject`` can share the same packages and won't have to download
them each time.

After asking the questions, ``zopeproject`` will download the
``zc.buildout`` package that will be used to build the sandbox, unless
``zc.buildout`` is already installed locally.  Then it will invoke
``zc.buildout`` to download Zope and its dependecies.  If you're doing
this for the first time or not sharing packages between different
projects, this may take a while.

When ``zopeproject`` is done, you will find a typical Python package
development environment in the ``MyZopeProj`` directory: the package
itself (``myzopeproj``) and a ``setup.py`` script.  There's also a
``bin`` directory that contains scripts, such as ``paster`` which can
be used to start the application::

  $ cd MyZopeProj
  $ bin/paster serve deploy.ini


Changes
=======

0.3.1 (2007-07-15)
------------------

* The buildout.cfg template was missing settings for the shared eggs
  directory and thew ``newest`` flag.

* Assemble the default path for the eggs directory in a
  Windows-friendly way.

0.3 (2007-07-14)
----------------

* Renamed to ``zopeproject``.

* Incorporated much of the ``grokproject`` 0.5.x infrastructure.  This
  makes it much more robust, especially when launching zc.buildout.

* Merged ``make-zope-app`` and ``deploy-zope-app`` back into one
  command: ``zopeproject``.

0.2 (2007-07-12)
-----------------

* Renamed to ``make-zope-app``.

* Split ``mkzopeapp`` into two commands: ``make-zope-app`` and
  ``deploy-zope-app``.

* No longer use ``zope.paste`` for the application factory.  Instead,
  each application that's created from the skeleton defines its own
  factory (which is reasonably small and gains flexibility).

* Get rid of the ``start<<Project>>`` script.  Simply use ``bin/paster
  serve deploy.ini`` for starting the server.

* Use the ``Paste#http`` server by default.

0.1 (2007-07-06)
-----------------

Initial release as ``mkzopeapp``
