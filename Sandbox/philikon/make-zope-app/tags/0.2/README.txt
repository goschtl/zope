With ``mkzopeapp`` you can start a new Zope-based web application from
scratch with one command::

  $ make-zope-app MyZopeProj

This will create a directory called ``MyZopeProj``.  In it, you will
find a typical development area for a Python package: a ``setup.py``
file and an empty package called ``myzopeproj`` in which you can now
place the code for your application.  Actually, the package is not
entirely empty, it contains a sample application configuration
(``configure.zcml``).

An application may easily be deployed (prepared for running) with
another command::

  $ deploy-zope-app MyZopeProj
  ...

You will be asked for the name and password of an initial
administrator user.  After that, you may run the application with the
``paster`` script::

  $ cd MyZopeProj
  $ bin/paster serve deploy.ini
