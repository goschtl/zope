Using Project Support
=====================

Project Support provides a set of scripts which help developers work with
individual zope projects.

develop.py
~~~~~~~~~~

The develop.py script is used to create a workspace from a zope project
checkout.  The script installs the development dependencies for the
project in a library folder, and any binary scripts in a scripts
folder.


Configuring Development Dependencies
------------------------------------

The script reads ``setup.cfg`` to read development dependencies.  In the
event that setup.cfg does not exist, the script will look for setup.cfg.in
and copy it to setup.cfg.  Keeping setup.cfg.in in source control is 
preferrable to setup.cfg, as develop.py will scribble path information on
the resulting setup.cfg file.

When develop.py is run, it will add additional entries to setup.cfg
specifying the library and scripts folders.  The minimal setup.cfg[.in] for
a project with development dependencies contains a single section with
a single entry.  For example:

  [development]
  depends = zope.event

The value of the ``depends`` key is a whitespace separated list of
project identifiers.  The project identifiers should match the names
listed in the individual project ``setup.py`` files.  In the example
above, setup.py in zope.event would specify

  name="zope.event"

as a parameter to the ``setup()`` call.


Setting up a workspace
----------------------

As an example, let us consider the zope.i18nmessageid project.  In
order to work on this project, we first check out the project trunk
from subversion:

  $ svn co svn+ssh://...@svn.zope.org/repos/main/zope.i18nmessageid\
     /trunk zope.i18nmessageid
  $ cd zope.i18nmessageid

As part of the checkout, subversion retrieves the develop.py script
via an svn:external.  We then configure the workspace for the project:

  $ python develop.py

Running develop.py with no parameters will create a ``lib`` and a
``bin`` directory in the working directory for libraries and scripts,
respectively.  Run develop.py with the --help parameter for
information on overriding these locations.

When develop.py runs, it creates the script and library locations,
bootstraps setuptools_ into the library, and retrieves any development
dependencies.  In the case of our zope.i18nmessageid example, the only
development dependency is zope.testing.

After the workspace has been configured, we run setup.py with the
develop target in order to retrieve any runtime dependencies.

  $ PYTHONPATH=lib/ python setup.py develop

In the case of zope.i18nmessage, this will retrieve zope.deprecation
and zope.interface, and place their eggs in the library directory.

While we currently have to specify the PYTHONPATH on the command line
(or export it as an environment variable), this will hopefully go away
real soon now.


Working with the package
------------------------

Running tests
-------------

Working with a dependency
-------------------------




.. _setuptools: http://peak.telecommunity.com/DevCenter/setuptools

