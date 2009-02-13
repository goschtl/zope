.. contents::

Quickstart
==========

You can start a new Zope-based web application from scratch with just
two commands::

  $ easy_install zopeproject
  $ zopeproject HelloWorld

The second command will ask you for a name and password for an
initial administrator user.  It will also ask you where to put the
Python packages ("eggs") that it downloads.  This way multiple
projects created with ``zopeproject`` can share the same packages and
won't have to download them each time (see also `Sharing eggs among
sandboxes`_ below).

(Note: Depending on how they installed Python, Unix/Linux users may
have to invoke ``easy_install`` with ``sudo``.  If that's not wanted
or possible, ``easy_install`` can be invoked with normal privileges
inside a `virtual-python`_ or workingenv_).

After asking these questions, ``zopeproject`` will download the
`zc.buildout`_ package that will be used to build the sandbox, unless
it is already installed locally.  Then it will invoke ``buildout`` to
download Zope and its dependencies.  If you're doing this for the first
time or not sharing packages between different projects, this may take
a while.

When ``zopeproject`` is done, you will find a typical Python package
development environment in the ``HelloWorld`` directory: the package
itself (``helloworld``) and a ``setup.py`` script.  There's also a
``bin`` directory that contains scripts, such as ``paster`` which can
be used to start the application::

  $ cd HelloWorld
  $ bin/paster serve deploy.ini

You may also use the ``helloworld-ctl`` script which works much like
the ``zopectl`` script from Zope instances::

  $ bin/helloworld-ctl foreground

After starting the application, you should now be able to go to
http://localhost:8080 and see the default start screen of Zope.  You
will also be able to log in with the administrator user account that
you specified earlier.

Notes for Windows users
-----------------------

Some packages required by Zope contain C extension modules.  There may
not always be binary Windows distributions available for these
packages.  In this case, setuptools will try to compile them from
source which will likely fail if you don't have a compiler such as the
Microsoft Visual C compiler installed.  Alternatively, you can install 
the free MinGW_ compiler:

1. Download ``MinGW-x.y.z.exe`` from http://www.mingw.org/ and run it 
   to do a full install into the standard location (ie. ``C:\MinGW``).

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

When installing packages from source, Python should now automatically 
use the MinGW compiler to build binaries.

Sharing eggs among sandboxes
----------------------------

A great feature of `zc.buildout`_ is the ability to share downloaded
Python packages ("eggs") between sandboxes.  This is achieved by
placing all eggs in a shared location.  zopeproject will ask for this
location each time.  The setting will become part of ``buildout.cfg``.

It could very well be that your shared eggs directory is different
from the suggested default value, so it would be good to avoid having
to type it in every time.  Furthermore, you may want to avoid having
system-dependent paths appear in ``buildout.cfg`` because they hinder
the repeatibility of the setup on other machines.

A way to solve these problems is to configure a user-specific default
eggs directory for buildout in your home directory:
``~/.buildout/default.cfg``::

  [buildout]
  eggs-directory = /home/philipp/eggs

zopeproject will understand that you have this default value and
change its own default when asking you for the eggs directory.  If you
just hit enter there (thereby accepting the default in
``~/.buildout/default.cfg``), the generated ``buildout.cfg`` will not
contain a reference to a path.

Command line options for zopeproject
====================================

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
  ``trunk`` below that. This checkin ignores any files and directories
  created by zc.buildout.

``-v``, ``--verbose``
  When this option is enabled, ``zopeproject`` won't hide the output
  of ``easy_install`` (used to install ``zc.buildout``) and the
  ``buildout`` command.

The sandbox
===========

What are the different files and directories for?
-------------------------------------------------

``deploy.ini``
  Configuration file for PasteDeploy_.  It defines which server
  software to launch and which WSGI application to invoke upon each
  request (which is defined in ``src/helloworld/startup.py``).  You
  may also define WSGI middlewares here.  Invoke ``bin/paster serve``
  with this file as an argument.

``debug.ini``
  Alternate configuration for PasteDeploy_ that configures 
  middleware which intercepts exceptions for interactive debugging.
  See `Debugging exceptions`_ below.

``zope.conf``
  This file will be read by the application factory in
  ``src/helloworld/startup.py``.  Here you can define which ZCML file
  the application factory should load upon startup, the ZODB database
  instance, an event log as well as whether developer mode is switched
  on or not.

``site.zcml``
  This file is referred to by ``zope.conf`` and will be loaded by the
  application factory.  It is the root ZCML file and includes
  everything else that needs to be loaded.  'Everything else' typically
  is just the application package itself, ``helloworld``, which then
  goes on to include its dependencies.  Apart from this, ``site.zcml``
  also defines the anonymous principal and the initial admin principal.

``setup.py``
  This file defines the egg of your application.  That definition
  includes listing the package's dependencies (mostly Zope eggs) and
  the entry point for the PasteDeploy_ application factory.

``buildout.cfg``
  This file tells `zc.buildout`_ what to do when the buildout is
  executed.  This mostly involves executing ``setup.py`` to enable the
  ``HelloWorld`` egg (which also includes downloading its
  dependencies), as well as installing PasteDeploy_ for the server.
  This files also refers to the shared eggs directory
  (``eggs-directory``) and determines whether buildout should check
  whether newer eggs are available online or not (``newest``).

``bin/``
  This directory contains all executable scripts, e.g for starting the
  application (``paster``), installing or reinstalling dependencies
  (``buildout``), or invoking the debug prompt (``helloworld-debug``).
  It also contains a script (``python``) that invokes the standard
  interpreter prompt with all packages on the module search path.

``src/``
  This directory contains the Python package(s) of your application.
  Normally there's just one package (``helloworld``), but you may add
  more to this directory if you like.  The ``src`` directory will be
  placed on the interpreter's search path by `zc.buildout`_.

``var/``
  The ZODB filestorage will place its files (``Data.fs``, lock files,
  etc.) here.

Renaming
--------

You can rename or move the sandbox directory any time you like.  Just
be sure to run ``bin/buildout`` again after doing so.  Renaming the
sandbox directory won't change the name of the egg, however. To do
that, you'll have to change the ``name`` parameter in ``setup.py``.

Sharing and archiving sandboxes
-------------------------------

You can easily share sandboxes with co-developers or archive them in a
version control system such as subversion.  You can theoretically
share or archive the whole sandbox directory, though it's recommended
**not to include** the following files and directories because they
can and will be generated by zc.buildout from the configuration files:

* ``bin/``

* ``parts/``

* ``develop-eggs/``

* all files in ``var/``

* all files in ``log/``

* ``.installed.cfg``

If you receive a sandbox thas has been archived (e.g. by checking it
out from a version control system), you will first have to bootstrap
it in order to obtain the ``bin/buildout`` executable.  To do that,
use the ``buildout`` script from any other sandbox on your machine::

  $ .../path/to/some/sandbox/bin/buildout bootstrap

Now the sandbox has its own ``bin/buildout`` script and can be
installed::

  $ bin/buildout

Developing
==========

First steps with your application
---------------------------------

After having started up Zope for the first time, you'll likely want to
start developing your web application.  Code for your application goes
into the ``helloworld`` package that was created by zopeproject in the
``src`` directory.

For example, to get a simple "Hello world!" message displayed, create
``src/helloworld/browser.py`` with the following contents::

  from zope.publisher.browser import BrowserPage

  class HelloPage(BrowserPage):
      def __call__(self):
          return "<html><body><h1>Hello World!</h1></body></html>"

Then all you need to do is hook up the page in ZCML.  To do that, add
the following directive towards the end of
``src/helloworld/configure.zcml``::

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
--------------------------------------

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
``src/helloworld/configure.zcml``::

  <include package="some.library" />

After having changed ``setup.py``, you would want the newly added
dependency to be downloaded and added to the search path of
``bin/paster``.  To do that, simply invoke the buildout::

  $ bin/buildout

Writing and running tests
-------------------------

Automated tests should be placed in Python modules.  If they all fit
in one module, the module should simply be named ``tests``.  If you
need many modules, create a ``tests`` package and put the modules in
there.  Each module should start with ``test`` (for example, the full
dotted name of a test module could be ``helloworld.tests.test_app``).

If you prefer to separate functional tests from unit tests, you can
put functional tests in an ``ftests`` module or package.  Note that
this doesn't matter to the test runner whatsoever, it doesn't care
about the location of a test case.

Each test module should define a ``test_suite`` function that
constructs the test suites for the test runner, e.g.::

  def test_suite():
      return unittest.TestSuite([
          unittest.makeSuite(ClassicTestCase),
          DocTestSuite(),
          DocFileSuite('README.txt', package='helloworld'),
          ])

To run all tests in your application's packages, simply invoke the
``bin/test`` script::

  $ bin/test

Functional tests
----------------

While unit test typically require no or very little test setup,
functional tests normally bootstrap the whole application's
configuration to create a real-life test harness.  The configuration
file that's responsible for this test harness is ``ftesting.zcml``.
You can add more configuration directives to it if you have components
that are specific to functional tests (e.g. mockup components).

To let a particular test run inside this test harness, simply apply
the ``helloworld.testing.FunctionalLayer`` layer to it::

  from helloworld.testing import FunctionalLayer
  suite.layer = FunctionalLayer

You can also simply use one of the convenience test suites in
``helloworld.testing``:

* ``FunctionalDocTestSuite`` (based on ``doctest.DocTestSuite``)

* ``FunctionalDocFileSuite`` (based on ``doctest.DocFileSuite``)

* ``FunctionalTestCase`` (based on ``unittest.TestCase``)

Debugging
=========

The interpreter prompt
----------------------

Use the ``bin/python`` script if you'd like test some components from
the interpreter prompt and don't need the component registrations nor
access to the ZODB.  If you do need those, go on to the next section.

The interactive debug prompt
----------------------------

Occasionally, it is useful to be able to interactively debug the state
of the application, such as walking the object hierarchy in the ZODB
or looking up components manually.  This can be done with the
interactive debug prompt, which is available under
``bin/helloworld-debug``::

  $ bin/helloworld-debug
  Welcome to the interactive debug prompt.
  The 'root' variable contains the ZODB root folder.
  The 'app' variable contains the Debugger, 'app.publish(path)' simulates a request.
  >>> 

You can now get a folder listing of the root folder, for example::

  >>> list(root.keys())
  [u'folder', u'file']

Debugging exceptions
--------------------

In case your application fails with an exception, it can be useful to
inspect the circumstances with a debugger.  This is possible with the
``z3c.evalexception`` WSGI middleware.  When an exception occurs in
your application, stop the process and start it up again, now using
the ``debug.ini`` configuration file::

  $ bin/paster serve debug.ini

When you then repeat the steps that led to the exception, you will see
the relevant traceback in your browser, along with the ability to view
the corresponding source code and to issue Python commands for
inspection.

If you prefer the Python debugger pdb_, replace ``ajax`` with ``pdb``
in the WSGI middleware definition in ``debug.ini``::

  [filter-app:main]
  use = egg:z3c.evalexception#pdb
  next = zope

Note: Even exceptions such as Unauthorized (which normally leads to a
login screen) or NotFound (which normally leads to an HTTP 404
response) will trigger the debugger.

Deploying
=========

Disabling debugging tools
-------------------------

Before deploying a zopeproject-based application, you should make sure
that any debugging tools are disabled.  In particular, this includes

* making sure there's no debugging middleware in ``deploy.ini``
  (normally these should be configured in ``debug.ini`` anyway),

* switching off ``developer-mode`` in ``zope.conf``,

* disabling the APIDoc tool in ``site.zcml``,

* disabling the bootstrap administrator principal in ``site.zcml``.

Linux/Unix
----------

You can use the ``helloworld-ctl`` script to start the server process
in daemon mode.  It works much like the ``apachectl`` tool as known
from the Apache HTTPD server or INIT scripts known from Linux::

  $ bin/helloworld-ctl start

To stop the server, issue::

  $ bin/helloworld-ctl stop

Other commands, such as ``status`` and ``restart`` are supported as
well.

Windows
-------

There's currently no particular support for deployment on Windows
other than what ``paster`` provides.  Integration with Windows
services, much like what could be found in older versions of Zope, is
planned.

Reporting bugs or asking questions about zopeproject
====================================================

zopeproject maintains a bugtracker and help desk on Launchpad:
https://launchpad.net/zopeproject

Questions can also be directed to the zope3-users mailinglist:
http://mail.zope.org/mailman/listinfo/zope3-users

Credits
=======

zopeproject is written and maintained by Philipp von Weitershausen.
It was inspired by the similar grokproject_ tool from the same author.

James Gardner, Martijn Faassen, Jan-Wijbrand Kolman and others gave
valuable feedback on the early prototype presented at EuroPython 2007.

Michael Bernstein gave valuable feedback and made many suggestions for
improvements.

zopeproject is distributed under the `Zope Public License,
v2.1`_. Copyright (c) by Zope Corporation and Contributors.


.. _virtual-python: http://peak.telecommunity.com/DevCenter/EasyInstall#creating-a-virtual-python
.. _workingenv: http://pypi.python.org/pypi/workingenv.py
.. _zc.buildout: http://pypi.python.org/pypi/zc.buildout
.. _MingW: http://www.mingw.org
.. _PasteDeploy: http://pythonpaste.org/deploy/
.. _listed on the Python Cheeseshop: http://pypi.python.org/pypi?:action=browse&c=515
.. _pdb: http://docs.python.org/lib/module-pdb.html
.. _grokproject: http://pypi.python.org/pypi/grokproject
.. _Zope Public License, v2.1: http://www.zope.org/Resources/ZPL
