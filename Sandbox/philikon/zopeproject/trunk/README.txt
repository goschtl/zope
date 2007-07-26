.. contents::

Quickstart
==========

You can start a new Zope-based web application from scratch with just
two commands::

  $ easy_install zopeproject
  $ zopeproject MyZopeProj

The second command will ask you for the name and password for an
initial administrator user.  It will also ask you where to put the
Python packages ("eggs") that it downloads.  This way multiple
projects created with ``zopeproject`` can share the same packages and
won't have to download them each time.

After asking the questions, ``zopeproject`` will download the
`zc.buildout`_ package that will be used to build the sandbox, unless
it is already installed locally.  Then it will invoke ``buildout`` to
download Zope and its dependencies.  If you're doing this for the first
time or not sharing packages between different projects, this may take
a while.

When ``zopeproject`` is done, you will find a typical Python package
development environment in the ``MyZopeProj`` directory: the package
itself (``myzopeproj``) and a ``setup.py`` script.  There's also a
``bin`` directory that contains scripts, such as ``paster`` which can
be used to start the application::

  $ cd MyZopeProj
  $ bin/paster serve deploy.ini

After starting the application with ``paster``, you should now be able
to go to http://localhost:8080 and see the default start screen of
Zope.  You will also be able to log in with the administrator user
account that you specified earlier.

Notes for Windows users
-----------------------

Some packages required by Zope contain C extension modules.  There may
not always be binary Windows distributions available for these
packages.  In this case, setuptools will try to compile them from
source which will likely fail if you don't have the Microsoft Visual C
compiler installed.  You can, however, install the free MinGW_
compiler:

1. Download ``MinGW-x.y.z.exe`` and rund it to do a full install into
   the standard location (``C:\MinGW``).

2. Tell Python to use the MinGW compiler by creating
   ``C:\Documents and Settings\YOUR USER\pydistutils.cfg``
   with the following contents::

     [build]
     compiler=mingw32

3. Let Python know about the MinGW installation and the
   ``pydistutils.cfg`` file.  To do that, go to the *Control Panel*,
   *System* section, *Advanced* tab and click on the *Environment
   variables* button.  Add the ``C:\MinGW\bin`` directory to your
   ``Path`` environment variable (individual paths are delimited by
   semicolons).  Also add another environment variable called ``HOME``
   with the following value::

     C:\Documents and Settings\YOUR USER

When installing packages from source, Python should now use the MinGW
compiler to build binaries.

.. _MingW: http://www.mingw.org

Command line options
====================

``--no-buildout``
  When invoked with this option, ``zopeproject`` will only create the
  project directory with the standard files in it, but it won't
  download and invoke ``zc.buildout``.

``--newer``
  This option enables the ``newest = true`` setting in
  ``buildout.cfg``.  That way, buildout will always check for newer
  versions of eggs online.  If, for example, you have outdated
  versions of your dependencies in your shared eggs directory, this
  switch will force the download of newer versions.  Note that you can
  always edit ``buildout.cfg`` to change this behaviour in an existing
  project area, or you can invoke ``bin/buildout`` with the ``-n``
  option.

``--svn-repository=REPOS``
  This option will import the project directory and the files in it
  into the given subversion repository and provide you with a checkout
  of the ``trunk``.  ``REPOS`` is supposed to be a repository path
  that is going to be created, along with ``tags``, ``branches`` and
  ``trunk`` below that.

``-v``, ``--verbose``
  When this option is enabled, ``zopeproject`` won't hide the output
  of ``easy_install`` (used to install ``zc.buildout``) and the
  ``buildout`` command.

What are the different files for?
=================================

``deploy.ini``
  Configuration file for PasteDeploy_.  It defines which server
  software to launch and which WSGI application to invoke upon each
  request (which is defined in ``myzopeproj/application.py``).  You
  may also define WSGI middlewares here.  Invoke ``bin/paster serve``
  with this file as an argument.

``zope.conf``
  This file will be read by the application factory in
  ``myzopeproj/application.py``.  Here you can define which ZCML file
  the application factory should load upon startup, the ZODB database
  instance, an event log as well as whether developer mode is switched
  on or not.

``site.zcml``
  This file is referred to by ``zope.conf`` and will be loaded by the
  application factory.  It is the root ZCML file and includes
  everything else that needs to be loaded.  That typically is just the
  application package itself, ``myzopeproj``, which then goes on to
  include its dependencies.  Apart from this, ``site.zcml`` also
  defines the anonymous principal and the initial admin principal.

``setup.py``
  This file defines the egg of your application.  That includes the
  package's dependencies (mostly Zope eggs) and the entry point for
  the PasteDeploy_ application factory.

``buildout.cfg``
  This file tells `zc.buildout`_ what to do when the buildout is
  executed.  This mostly involves executing ``setup.py`` to enable the
  ``MyZopeProj`` egg (which also includes downloading its
  dependencies), as well as installing PasteDeploy_ for the server.
  This files also refers to the shared eggs directory
  (``eggs-directory``) and determines whether buildout should check
  whether newer eggs are available online or not (``newest``).

First steps with your application
=================================

After having started up Zope for the first time, you'll likely want to
start developing your web application.  Code for your application goes
into the ``myzopeproj`` package that was created by zopeproject.

For example, to get a simple "Hello world!" message displayed, create
``myzopeproj/browser.py`` with the following contents::

  from zope.publisher.browser import BrowserPage

  class HelloPage(BrowserPage):
      def __call__(self):
          return "<html><body><h1>Hello World!</h1></body></html>"

Then all you need to do is hook up the page in ZCML.  To do that, add
the following directive towards the end of ``myzopeproj/configure.zcml``::

  <browser:page
      for="*"
      name="hello"
      class=".browser.HelloPage"
      permission="zope.Public"
      />

Note that you'll likely need to define the ``browser`` namespace
prefix at the top of the file::

  <configure xmlns="http://namespaces.zope.org/zope"
             xmlns:browser="http://namespaces.zope.org/browser"
             >

After having restarted the application using ``paster serve``, you can
visit http://localhost:8080/hello to see the page in action.

Adding dependencies to the application
======================================

The standard ``setup.py`` and ``configure.zcml`` files list a set of
standard dependencies that are typical for most Zope applications.
You may obviously remove things from this list, but typically you'll
want to re-use more libraries that others have written.  Many, if not
most, of additional Zope and third party libraries are `listed on the
Python Cheeseshop`_.

Let's say you wanted to reuse the ``some.library`` package in your
application.  The first step would be to add it to the list of
dependencies in ``setup.py`` (``install_requires``).  If this package
defined any Zope components, you would probably also have to load its
ZCML configuration by adding the following line to
``myzopeproj/configure.zcml``::

  <include package="some.library" />

After having changed ``setup.py``, you would want the newly added
dependency to be downloaded and added to the search path of
``bin/paster``.  To do that, simply invoke the buildout::

  $ bin/buildout


Changes
=======

0.3.3 (unreleased)
------------------

* More improvements to the README.txt file.

0.3.2 (2007-07-17)
------------------

* If the user already has a default eggs directory set in
  ``~/.buildout/default.cfg``, it is used as the default value for the
  eggs directory.

* Greatly improved the README.txt file.

0.3.1 (2007-07-15)
------------------

* The ``buildout.cfg`` template was missing settings for the shared
  eggs directory and thew ``newest`` flag.

* Assemble the default path for the eggs directory in a
  Windows-friendly way.

0.3 (2007-07-14)
----------------

* Renamed to ``zopeproject``.

* Incorporated much of the grokproject_ 0.5.x infrastructure.  This
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


.. _zc.buildout: http://cheeseshop.python.org/pypi/zc.buildout
.. _PasteDeploy: http://pythonpaste.org/deploy/
.. _listed on the Python Cheeseshop: http://cheeseshop.python.org/pypi?:action=browse&c=515
.. _grokproject: http://cheeseshop.python.org/pypi/grokproject
