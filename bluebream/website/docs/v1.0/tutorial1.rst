.. _tut1-tutorial:

Tutorial --- Part 1
===================

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

.. _tut1-introduction:

Introduction
------------

In the :ref:`started-getting` chapter you learned how to install
BlueBream and create a new project using the ``bluebream`` project
template.  In this tutorial, you can learn creating a simple ticket
collector application.  This will help you to get more familiar with
the concepts of BlueBream.

Here is the user stories for the ticket collector application:

1. Any number of tickets can be added to one collector.

2. Each ticket will be added with a description and one initial
   comment.

3. Additional comments can be added to tickets.

This is the first part of the tutorial.  After completing this
chapter, you should be able to:

- Understand the project directory structure
- Use Buildout and edit Buildout configuration
- Create content objects and interfaces
- Use form generation tool (zope.formlib)

.. note::

   The examples in this documentation can be downloaded from here:
   http://download.zope.org/bluebream/examples/ticketcollector-1.0.0.tar.bz2

.. _tut1-new-project:

Starting a new project
----------------------

Using the *bluebream* project template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section we will create the directory layout for our ticket
collector application.  I will assume that you have already installed
``bluebream`` using the ``easy_install bluebream`` command as
mentioned in the :ref:`started-getting` chapter.  We are going to use
the project name ``ticketcollector`` and namespace package name
``tc``.  Let's create the project directory layout for
``ticketcollector``::

  $ paster create -t bluebream
  Selected and implied templates:
    bluebream#bluebream  A BlueBream project, base template
  
  Enter project name: ticketcollector
  Variables:
    egg:      ticketcollector
    package:  ticketcollector
    project:  ticketcollector
  Enter namespace_package (Namespace package name) ['ticketcollector']: tc
  Enter main_package (Main package name (under the namespace)) ['main']: 
  Enter interpreter (Name of custom Python interpreter) ['breampy']: 
  Enter version (Version (like 0.1)) ['0.1']: 
  Enter description (One-line description of the package) ['']: Ticket Collector
  Enter long_description (Multi-line description (in reST)) ['']: An issue tracking application
  Enter keywords (Space-separated keywords/tags) ['']: 
  Enter author (Author name) ['']: Baiju M
  Enter author_email (Author email) ['']: baiju@example.com
  Enter url (URL of homepage) ['']: 
  Enter license_name (License name) ['']: ZPL
  Enter zip_safe (True/False: if the package can be distributed as a .zip file) [False]: 
  Creating template bluebream
  Creating directory ./ticketcollector
    Copying bootstrap.py to ./ticketcollector/bootstrap.py
    Copying buildout.cfg_tmpl to ./ticketcollector/buildout.cfg
    Copying debug.ini_tmpl to ./ticketcollector/debug.ini
    Copying deploy.ini_tmpl to ./ticketcollector/deploy.ini
    Recursing into etc
      Creating ./ticketcollector/etc/
      Copying site.zcml_tmpl to ./ticketcollector/etc/site.zcml
    Copying setup.py_tmpl to ./ticketcollector/setup.py
    Recursing into src
      Creating ./ticketcollector/src/
      Recursing into +namespace_package+
        Creating ./ticketcollector/src/tc/
        Recursing into +main_package+
          Creating ./ticketcollector/src/tc/main/
          Copying __init__.py to ./ticketcollector/src/tc/main/__init__.py
          Copying configure.zcml_tmpl to ./ticketcollector/src/tc/main/configure.zcml
          Copying debug.py to ./ticketcollector/src/tc/main/debug.py
          Copying securitypolicy.zcml_tmpl to ./ticketcollector/src/tc/main/securitypolicy.zcml
          Copying startup.py to ./ticketcollector/src/tc/main/startup.py
          Recursing into tests
            Creating ./ticketcollector/src/tc/main/tests/
            Copying __init__.py to ./ticketcollector/src/tc/main/tests/__init__.py
            Copying ftesting.zcml_tmpl to ./ticketcollector/src/tc/main/tests/ftesting.zcml
            Copying tests.py_tmpl to ./ticketcollector/src/tc/main/tests/tests.py
          Recursing into welcome
            Creating ./ticketcollector/src/tc/main/welcome/
            Copying __init__.py to ./ticketcollector/src/tc/main/welcome/__init__.py
            Copying app.py to ./ticketcollector/src/tc/main/welcome/app.py
            Copying configure.zcml_tmpl to ./ticketcollector/src/tc/main/welcome/configure.zcml
            Copying ftests.txt_tmpl to ./ticketcollector/src/tc/main/welcome/ftests.txt
            Copying index.pt to ./ticketcollector/src/tc/main/welcome/index.pt
            Copying interfaces.py to ./ticketcollector/src/tc/main/welcome/interfaces.py
            Recursing into static
              Creating ./ticketcollector/src/tc/main/welcome/static/
              Copying logo.png to ./ticketcollector/src/tc/main/welcome/static/logo.png
              Copying style.css to ./ticketcollector/src/tc/main/welcome/static/style.css
            Copying views.py to ./ticketcollector/src/tc/main/welcome/views.py
        Copying __init__.py to ./ticketcollector/src/tc/__init__.py
      Recursing into +package+.egg-info
        Creating ./ticketcollector/src/ticketcollector.egg-info/
        Copying PKG-INFO to ./ticketcollector/src/ticketcollector.egg-info/PKG-INFO
    Recursing into templates
      Creating ./ticketcollector/templates/
      Copying zope_conf.in to ./ticketcollector/templates/zope_conf.in
    Recursing into var
      Creating ./ticketcollector/var/
      Recursing into filestorage
        Creating ./ticketcollector/var/filestorage/
        Copying README.txt to ./ticketcollector/var/filestorage/README.txt
      Recursing into log
        Creating ./ticketcollector/var/log/
        Copying README.txt to ./ticketcollector/var/log/README.txt
    Copying versions.cfg to ./ticketcollector/versions.cfg
  Running /usr/bin/python setup.py egg_info

As you can see above we have provided most of the project details.
The values you provided here may be changed later, however changing
the package name or the namespace package name may not be as easy as
changing the description because the name and namespace package might
be referred to from many places.

Organize the new package
~~~~~~~~~~~~~~~~~~~~~~~~

If you change directory to ``ticketcollector`` you can see a few
directories and files::

  jack@computer:/projects/ticketcollector$ ls -CF
  bootstrap.py  debug.ini   etc/      src/        var/
  buildout.cfg  deploy.ini  setup.py  templates/  versions.cfg

Once the project directory layout is ready you can add it to your
version control system.  You **should not** add
``src/ticketcollector.egg-info`` directory as it is generated
automatically by setuptools.  Here is an example using `bzr
<http://bazaar.canonical.com/en/>`_::

  jack@computer:/projects/ticketcollector$ rm -fr src/ticketcollector.egg-info/
  jack@computer:/projects/ticketcollector$ bzr init
  Created a standalone tree (format: 2a)
  jack@computer:/projects/ticketcollector$ bzr add *
  adding bootstrap.py
  adding buildout.cfg
  adding debug.ini
  ...
  jack@computer:/projects/ticketcollector$ bzr ci -m "Initial import"
  Committing to: /projects/ticketcollector/
  added bootstrap.py
  added buildout.cfg
  ...
  Committed revision 1.

Adding the project to a version control system is an optional but
recommended step.  You now have a valid source code distribution of
your project that after building will produce a running application.
The project is now completely independent of the ``bluebream``
distribution, it's only purpose is to help us get to this point.  The
project now contains all mechanisms required to install the
dependencies from the Internet and setting up the application.

Bootstrapping the project
~~~~~~~~~~~~~~~~~~~~~~~~~

The next step is to install Buildout.  The purpose of Buildout is to
automate the building of Python applications from their bare source
code form.  The only basic requirement for Buildout is a Python
installation.  BlueBream provides a bootstrapping script to install
Buildout and to set up the project directory for running it.  This
bootstrap script is named ``bootstrap.py`` and will do these things:

- Download and install ``setuptools`` package from PyPI

- Download and install ``zc.buildout`` package from PyPI

- Create a directory structure eg:- bin/ eggs/ parts/ develop-eggs/

- Create a script inside the ``bin`` directory named ``buildout``

When you run ``bootstrap.py`` you can see that it creates a few
directories and the ``bin/buildout`` script as mentioned earlier::

  jack@computer:/projects/ticketcollector$ python bootstrap.py
  Creating directory '/projects/ticketcollector/bin'.
  Creating directory '/projects/ticketcollector/parts'.
  Creating directory '/projects/ticketcollector/develop-eggs'.
  Creating directory '/projects/ticketcollector/eggs'.
  Generated script '/projects/ticketcollector/bin/buildout'.

- The ``bin`` directory is where Buildout install all the executable
  scripts.

- The ``eggs`` directory is where Buildout install Python eggs

- The ``parts`` is where Buildout save all output generated by buildout.
  Buildout expects you to not change anything inside parts directory
  as it is auto generated by Buildout.

- The ``develop-eggs`` directory is where Buildout save links to all
  locally developped Python eggs.

Buildout configuration
~~~~~~~~~~~~~~~~~~~~~~

After bootstrapping the project you can build your application.  All
the steps you did so far is only required once per project, but
running buildout is required whenever you make changes to the
buildout configuration.  You are now ready to run ``bin/buildout`` to
build the application, but before doing this let's have a look at the
content of ``buildout.cfg``::

  [config]
  site_zcml = etc/site.zcml
  blob = var/blob
  filestorage = var/filestorage
  log = var/log

  [buildout]
  develop = .
  extends = versions.cfg
  parts = app
          zope_conf
          test

  [app]
  recipe = zc.recipe.egg
  eggs = ticketcollector
         z3c.evalexception>=2.0
         Paste
         PasteScript
         PasteDeploy
  interpreter = breampy

  [zope_conf]
  recipe = collective.recipe.template
  input = templates/zope_conf.in
  output = etc/zope.conf

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector

The buildout configuration file is divided into multiple sections
called *parts*.  The main part is called ``[buildout]``, and that is
given as the second part in the above configuration file.  We have
added a part named ``[config]`` for convenience which includes some
common options referred to from other places.  Each part will be
handled by the Buildout plugin mechanism called recipes except for
``[buildout]`` and ``[config]``.  ``[buildout]`` is handled specially
by Buildout as it contains general settings and ``[config]`` only
contains options used for other parts.

We will look at each part here.  Let's start with ``[config]``::

  [config]
  site_zcml = etc/site.zcml
  blob = var/blob
  filestorage = var/filestorage
  log = var/log

The ``[config]`` is kind of abstract part which exists for
convenience to hold options used by other parts and is an idiom in
many projects using Buildout.  In this configuration the options
provided are _not_ used by other parts directly, but all are used in
one template given in the ``[zope_conf]`` part.  Here is details
about each options:

- ``site_zcml`` -- this is the location where final ``site.zcml``
  file is residing.

- ``blob`` -- location where ZODB blob files are stored.

- ``filestorage`` -- ZODB data files are stored here.

- ``log`` -- All log files goes here.

Let's look at the main ``[buildout]`` part::

  [buildout]
  develop = .
  extends = versions.cfg
  parts = app
          zope_conf
          test

The first option (``develop``) tells buildout that, the current
directory is a Python distribution source, i.e., it contains a
``setup.py`` file.  Buildout will inspect the ``setup.py`` and create
a develop egg link inside the ``develop-eggs`` directory.  The link
file should contain path to the location where the Python package is
residing.  So buildout will make sure that the packages is always
importable.  The value of the ``develop`` option could be a relative path
as given above or absolute path to some directory.  You can also add
multiple lines to ``develop`` option with different paths.

The ``extends`` option tells buildout to include the full content of
``versions.cfg`` file as part the configuration.  The
``versions.cfg`` is another Buildout configuration file of the same
format as buildout.cfg and contains the release numbers of different
dependencies.  You can add multiple lines to ``extends`` option to
include multiple configuration files.

The ``parts`` option list all the parts to be built by Buildout.
Buildout expects a recipe for each parts listed here.  Which means
that you cannot include ``config`` part here as it doesn't have any
recipe associated with it.

Now let's look at the ``app`` part::

  [app]
  recipe = zc.recipe.egg
  eggs = ticketcollector
         z3c.evalexception>=2.0
         Paste
         PasteScript
         PasteDeploy
  interpreter = breampy

This part takes care of all the eggs required for the application to
function.  The `zc.recipe.egg
<http://pypi.python.org/pypi/zc.recipe.egg>`_ is an advanced Buildout
recipe with many features to deal with egg.  Majority of the
dependencies will come as part of the main application egg.  The
option ``eggs`` list all the eggs.  The first egg,
``ticketcollector`` is the main locally developing egg.  The last
option, ``interpreter`` specify the name of custom interpreter
created by this part.  The custom interpreter contains the paths to
all eggs listed here and its dependencies.

The ``[zope_conf]`` part creates the ``zope.conf`` from a template::

  [zope_conf]
  recipe = collective.recipe.template
  input = templates/zope_conf.in
  output = etc/zope.conf

This part is fairly self explanatory, it creates a ``zope.conf`` file
from the template file ``templates/zope_conf.in``.  This
`collective.recipe.template recipe
<http://pypi.python.org/pypi/collective.recipe.template>`_ is very
popular among Buildout users.  Here is the template file
(``templates/zope_conf.in``)::

  # Identify the component configuration used to define the site:
  site-definition ${config:site_zcml}

  <zodb>


      <filestorage>
        path ${config:filestorage}/Data.fs
        blob-dir ${config:blob}
      </filestorage>

  # Uncomment this if you want to connect to a ZEO server instead:
  #  <zeoclient>
  #    server localhost:8100
  #    storage 1
  #    # ZEO client cache, in bytes
  #    cache-size 20MB
  #    # Uncomment to have a persistent disk cache
  #    #client zeo1
  #  </zeoclient>
  </zodb>

  <eventlog>
    # This sets up logging to both a file and to standard output (STDOUT).
    # The "path" setting can be a relative or absolute filesystem path or
    # the tokens STDOUT or STDERR.

    <logfile>
      path ${config:log}/z3.log
      formatter zope.exceptions.log.Formatter
    </logfile>

    <logfile>
      path STDOUT
      formatter zope.exceptions.log.Formatter
    </logfile>
  </eventlog>

  # Comment this line to disable developer mode.  This should be done in
  # production
  devmode on

The last part creates the test runner::

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector

The testrunner recipe creates a test runner using the ``zope.testing``
module.  The only mandatory option is ``eggs`` where you can specify
the eggs.

Building the project
~~~~~~~~~~~~~~~~~~~~

Now you can run the ``bin/buildout`` command.  It will take some time
to download all packages from PyPI.  When you run buildout, it will
show something like this::

  jack@computer:/projects/ticketcollector$ ./bin/buildout
  Develop: '/projects/ticketcollector/.'
  Installing app.
  Generated script '/projects/ticketcollector/bin/paster'.
  Generated interpreter '/projects/ticketcollector/bin/breampy'.
  Installing zope_conf.
  Installing test.
  Generated script '/projects/ticketcollector/bin/test'.

In the above example, all eggs are already available in the eggs
folder, otherwise it will download and install eggs.  The buildout
also created three more scripts inside ``bin`` directory.

- The ``paster`` command can be used to run web server.

- The ``breampy`` command provides a custom Python interpreter with
  all eggs included in path.

- The ``test`` command can be used to run the test runner.

Now we have a project source where we can continue developing this
application.

The site definition
-------------------

BlueBream use ZCML for application specific configuration.  ZCML is
an XML-based declarative configuration language.  As you have seen
already in ``zope.conf`` the main configuration is located at
``etc/site.zcml``.  Here is the default listing::

  <configure
     xmlns="http://namespaces.zope.org/zope">

    <include package="zope.component" file="meta.zcml" />
    <include package="zope.security" file="meta.zcml" />
    <include package="zope.publisher" file="meta.zcml" />
    <include package="zope.i18n" file="meta.zcml" />
    <include package="zope.browserresource" file="meta.zcml" />
    <include package="zope.browsermenu" file="meta.zcml" />
    <include package="zope.browserpage" file="meta.zcml" />
    <include package="zope.securitypolicy" file="meta.zcml" />
    <include package="zope.principalregistry" file="meta.zcml" />
    <include package="zope.app.publication" file="meta.zcml" />
    <include package="zope.app.form.browser" file="meta.zcml" />
    <include package="zope.app.container.browser" file="meta.zcml" />

    <include package="zope.publisher" />
    <include package="zope.component" />
    <include package="zope.traversing" />
    <include package="zope.site" />
    <include package="zope.annotation" />
    <include package="zope.container" />
    <include package="zope.componentvocabulary" />
    <include package="zope.formlib" />
    <include package="zope.app.appsetup" />
    <include package="zope.app.security" />
    <include package="zope.app.publication" />
    <include package="zope.app.form.browser" />
    <include package="zope.app.basicskin" />
    <include package="zope.browsermenu" />
    <include package="zope.principalregistry" />
    <include package="zope.authentication" />
    <include package="zope.securitypolicy" />
    <include package="zope.login" />
    <include package="zope.app.zcmlfiles" file="menus.zcml" />
    <include package="zope.app.authentication" />
    <include package="zope.app.security.browser" />

    <include package="tc.main" />

  </configure>

The main configuration, ``site.zcml`` include other configuration
files specific to packages.  The ZCML has some directives like
`include``, ``page``, ``defaultView`` etc. available through various
XML-namespaces.  In the ``site.zcml`` the default XML-namespace is
``http://namespaces.zope.org/zope``.  If you look at the top of
site.zcml, you can see the XML-namespace refered to like this::

  <configure
   xmlns="http://namespaces.zope.org/zope">

The ``include`` directive is available in
``http://namespaces.zope.org/zope`` namespace.  If you look at other
configuration files, you can see some other namespaces like
``http://namespaces.zope.org/browser`` used which has some directives
like ``page``.

At the end of ``site.zcml``, project specific configuration files are
included like this.  This will cause to load
``src/tc/collector/configure.zcml`` file::

  <include package="tc.main" />

Also you can define common configuration for your entire application
in the ``site.zcml``.  The content of ``src/tc/collector/configure.zcml``
will look like this::

  <configure
     xmlns="http://namespaces.zope.org/zope"
     xmlns:browser="http://namespaces.zope.org/browser"
     i18n_domain="ticketcollector">
  
    <include file="securitypolicy.zcml" />
  
    <!-- The following registration (defaultView) register 'index' as
         the default view for a container.  The name of default view
         can be changed to a different value, for example, 'index.html'.
         More details about defaultView registration is available here:
         http://bluebream.zope.org/doc/1.0/howto/defaultview.html
         -->
  
    <browser:defaultView
       for="zope.container.interfaces.IContainer"
       name="index"
       />
  
    <!-- To remove the sample application delete the following line
         and remove the `welcome` folder from this directory.
         -->
    <include package=".welcome" />
  
  </configure>

The ``securitypolicy.zcml`` is where you can define the security
policies.  As you can see in the ``configure.zcml``, it includes
``welcome``.  By default, if you include a package without mentioning
the configuration file, it will include ``configure.zcml``.

.. _tut1-package-meta-data:

The package meta-data
---------------------

BlueBream use :term:`Setuptools` to distribute the application
package.  However, you could easily replace it with
:term:`Distribute`.

Your ticketcollector package's setup.py will look like this::

  from setuptools import setup, find_packages

  setup(name='ticketcollector',
        version='0.1',
        description='Ticket Collector',
        long_description="""\
  A ticket collector application""",
        # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[],
        keywords='',
        author='Baiju M',
        author_email='baiju@example.com',
        url='',
        license='ZPL',
        package_dir={'': 'src'},
        packages=find_packages('src'),
        namespace_packages=['tc',],
        include_package_data=True,
        zip_safe=False,
        install_requires=['setuptools',
                          'zope.securitypolicy',
                          'zope.component',
                          'zope.annotation',
                          'zope.app.dependable',
                          'zope.app.appsetup',
                          'zope.app.content',
                          'zope.publisher',
                          'zope.app.broken',
                          'zope.app.component',
                          'zope.app.generations',
                          'zope.app.error',
                          'zope.app.interface',
                          'zope.app.publisher',
                          'zope.app.security',
                          'zope.app.form',
                          'zope.app.i18n',
                          'zope.app.locales',
                          'zope.app.zopeappgenerations',
                          'zope.app.principalannotation',
                          'zope.app.basicskin',
                          'zope.app.rotterdam',
                          'zope.app.folder',
                          'zope.app.wsgi',
                          'zope.formlib',
                          'zope.i18n',
                          'zope.app.pagetemplate',
                          'zope.app.schema',
                          'zope.app.container',
                          'zope.app.debug',
                          'z3c.testsetup',
                          'zope.app.testing',
                          'zope.testbrowser',
                          'zope.login',
                          'zope.app.zcmlfiles',
                          ],
        entry_points = """
        [paste.app_factory]
        main = tc.main.startup:application_factory

        [paste.global_paster_command]
        shell = tc.main.debug:Shell
        """,
        )

Most of the details in the ``setup.py`` is what you're given when
creating the project from template.  In the ``install_requires``
keyword argument, you can list all dependencies for the package.
There are two entry points, the first one is used by PasteDeploy to
find the WSGI application factory.  The second entry point register a
sub-command for ``paster`` script named ``shell``.

Running Tests
-------------

BlueBream use `zope.testing
<http://pypi.python.org/pypi/zope.testing>`_ as the main framework for
automated testing.  Along with **zope.testing**, you can use Python's
``unittest`` and ``doctest`` modules.  Also there is a functional
testing module called `zope.testbrowser
<http://pypi.python.org/pypi/zope.testbrowser>`_ . To setup the test
cases, layers etc. BlueBream use the `z3c.testsetup
<http://pypi.python.org/pypi/z3c.testsetup>`_ package.

BlueBream use the Buildout recipe called `zc.recipe.testrunner
<http://pypi.python.org/pypi/zc.recipe.testrunner>`_ to generate test
runner script.

If you look at the buildout configuration, you can see the test
runner part::

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector

The testrunner recipe creates a test runner using ``zope.testing``
module.  The only mandatory option is ``eggs`` where you can specify
the eggs.

To run all test cases, use the ``bin/test`` command::

  jack@computer:/projects/ticketcollector$ bin/test

This command will find all the test cases and run it.

.. _tut1-app-object:

Creating the application object
-------------------------------

Container objects
~~~~~~~~~~~~~~~~~

In this section we will explore one of the main concepts in BlueBream
called **container object**.  As mentioned earlier BlueBream use an
object database called ZODB to store your Python objects.  You can
think of an object database as a container which contains objects,
the inner object may be another container which contains other
objects.

The object hierarchy may look like this::

  +-----------------------+
  |                       |
  |   +---------+  +--+   |
  |   |         |  +--+   |
  |   |  +--+   |         |
  |   |  +--+   |         |
  |   +---------+    +--+ |
  |                  +--+ |
  +-----------------------+

BlueBream will take care of the persistence of the objects.  In order
to make a custom object persistent the object class will have to
inherit from ``persistent.Persistent``.

Some classes in BlueBream that inherits ``persistent.Persistent``:

- ``zope.container.btree.BTreeContainer``
- ``zope.container.folder.Folder``
- ``zope.site.folder.Folder``

When you inherit from any of these classes the instances of that
class will be persistent.  The second thing you need to do to make it
persistent is to add the object to an existing container object.  You
can experiment with this from the debug shell provided by BlueBream.
But before you try that out create a container class somewhere in
your code which can be imported later.  You can add this definition
to the ``src/tc/collector/__init__.py`` file (Delete it after the
experiment)::

  from zope.container.btree import BTreeContainer

  class MyContainer(BTreeContainer):
      pass

Then open the debug shell as given below::

  $ ./bin/paster shell debug.ini
  ...
  Welcome to the interactive debug prompt.
  The 'root' variable contains the ZODB root folder.
  The 'app' variable contains the Debugger, 'app.publish(path)' simulates a request.
  >>>

The name ``root`` refers to the top-level container in the database.
You can import your own container class, create an instance and add
it to the root folder::

  >>> from tc.main import MyContainer
  >>> root['c1'] = MyContainer()

ZODB is a transactional database so you will have to commit your
changes in order for them to be performed.  To commit your changes
use the function ``transaction.commit`` as described below::

  >>> import transaction
  >>> transaction.commit()

Now you can exit the debug prompt and open it again and see that you
can access the persistent object again::

  $ ./bin/paster shell debug.ini
  ...
  Welcome to the interactive debug prompt.
  The 'root' variable contains the ZODB root folder.
  The 'app' variable contains the Debugger, 'app.publish(path)' simulates a request.
  >>> root['c1']
  <tc.main.MyContainer object at 0x96091ac>

Persisting random objects like this is not a particulary good idea.
The next section will explain how to create a formal schema for your
objects.  Now you can delete the object and remove the
``MyContainer`` class definition from ``src/tc/collector/__init__.py``.
You can delete the object like this::

  >>> del(root['c1'])
  >>> import transaction
  >>> transaction.commit()

Declaring an Interface
~~~~~~~~~~~~~~~~~~~~~~

.. note::

   If you have never worked with ``zope.interface`` before, we
   recommend that you read through the :ref:`man-interface` chapter
   in the manual before proceding.

As the first step for creating the main application container object
which is going to hold all other objects, you need to create an
interface.  You can name the main application container interface as
``ICollector``.  To make this a container object, inherit from
``zope.container.interfaces.IContainer`` or any derived interfaces.
It is recommended add a site manager inside the main application
container.  In order to add a site manager later, it is recommend to
inherit from ``zope.site.interfaces.IFolder`` interface.  The
``IFolder`` is inheriting from ``IContainer``.

You can create a new Python package named ``collector`` inside
``src/tc`` like this::

  $ mkdir src/tc/collector
  $ echo "# Python Package" > src/tc/collector/__init__.py

You can create a file named ``src/tc/collector/interfaces.py`` to add
new interfaces like this::

  from zope.site.interfaces import IFolder
  from zope.schema import TextLine
  from zope.schema import Text

  class ICollector(IFolder):
      """The main application container"""

      name = TextLine(
          title=u"Name",
          description=u"Name of application container",
          default=u"",
          required=True)

      description = Text(
          title=u"Description",
          description=u"Description of application container",
          default=u"",
          required=False)

The interface defined here is your schema for the object.  There are
two fields defined in the schema.  The first one is ``name`` and the
second one is ``description``.  The schema is also can be used to
auto-generate web forms.

Implementing Interface
~~~~~~~~~~~~~~~~~~~~~~

Schema is kind of blueprint for your objects, schema define the
contracts for the objects.  Once you have schema ready, you can
create some concrete classes which implement the schema.

Next, you need to implement this interface.  To implement
``IContainer``, you can inherit from ``zope.site.folder.Folder``.
You can create the implementation in
``src/tc/collector/ticketcollector.py``::

  from zope.interface import implements
  from zope.site.folder import Folder

  from tc.collector.interfaces import ICollector

  class Collector(Folder):
      """A simple implementation of a collector using B-Tree
      Container."""

      implements(ICollector)

      name = u""
      description = u""

To declare a class is implementing a particular interface, you can
use ``implements`` function.  The class also provides defaults values
for attributes.

Registering components
~~~~~~~~~~~~~~~~~~~~~~

Once the interfaces and its implementations are ready.  You can do
the configuration in ZCML.  Open the ``src/tc/collector/configure.zcml``
file to edit, then mark the ``ICollector`` as a content component::

  <interface
     interface="tc.collector.interfaces.ICollector"
     type="zope.app.content.interfaces.IContentType"
     />

The ``zope.app.content.interfaces.IContentType`` represents a content
type.  If an **interface** provides ``IContentType`` interface type,
then all objects providing the **interface** are considered content
objects.

To set annotations for collector objects, we need to mark it as
implementing ``zope.annotation.interfaces.IAttributeAnnotatable``
marker interface.  Also this configuration declare that ``Collector``
class implements ``zope.container.interfaces.IContentContainer``.
These two classes are marker interfaces.  An interface used to
declare that a particular object belongs to a special type is called
marker interface.  Marker interface won't be having any attribute or
method.

::

  <class class="tc.collector.ticketcollector.Collector">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <implements
       interface="zope.container.interfaces.IContentContainer"
       />
    <require
       permission="zope.ManageContent"
       interface="tc.collector.interfaces.ICollector"
       />
    <require
       permission="zope.ManageContent"
       set_schema="tc.collector.interfaces.ICollector"
       />
  </class>

The ``class`` directive is a complex directive.  There are
subdirective like ``implements`` and ``require`` below the ``class``
directive.  The above ``class`` directive also declared permission
setting for ``Collector``.

A view for adding collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now the content component is ready to use.  You need a web page from
where we can add the ticket collector.  You can use ``zope.formlib``
package to create a form.  You can add the view class definition
inside ``src/tc/collector/views.py`` like this::

  from zope.site import LocalSiteManager
  from zope.formlib import form

  from tc.collector.interfaces import ICollector

  from tc.collector.ticketcollector import Collector

  class AddTicketCollector(form.AddForm):

      form_fields = form.Fields(ICollector)

      def createAndAdd(self, data):
          name = data['name']
          description = data.get('description', u'')
          collector = Collector()
          collector.name = name
          collector.description = description
          self.context[name] = collector
          collector.setSiteManager(LocalSiteManager(collector))
          self.request.response.redirect(".")

The ``createAndAdd`` function will be called when used submit *Add*
button from web form.  The second last line is very important::

  collector.setSiteManager(LocalSiteManager(collector))

This line add a site manager to the collector, so that it can be used
as a persistent component registry to register local components like
local utilities.

As you have already seen in the previous chapter, ``browser:page``
directive is used for registering pages.  You can give the name as
``add_ticket_collector`` and register it for
``zope.site.interfaces.IRootFolder``.  Add these lines to
``src/tc/collector/configure.zcml``::

  <browser:page
     for="zope.site.interfaces.IRootFolder"
     name="add_ticket_collector"
     permission="zope.ManageContent"
     class="tc.collector.views.AddTicketCollector"
     />

The package development is completed now.  This package is not
included from the main package yet.  To include this package from the
main package (``tc.main``), you need to modify the
``src/tc/main/configure.zcml`` and add this line before
``</configure>``::

  <include package="tc.collector" />

Now you can access the URL:
http://localhost:8080/@@add_ticket_collector .  It should display a
form where you can enter details like ``name`` and ``description``.
You can enter the ``name`` as ``mycollector``, after entering data,
submit the form.

You can see the file size of ``var/filestorage/Data.fs`` is
increasing as objects are getting added.  The ``Data.fs`` is where
the data is physically stored.

You can also confirm the object is actually saved into database from
Python shell.  If you go to Python shell and try to access the root
object, you can see that it has the object you added::

  jack@computer:/projects/ticketcollector$ ./bin/paster shell debug.ini
  ...
  Welcome to the interactive debug prompt.
  The 'root' variable contains the ZODB root folder.
  The 'app' variable contains the Debugger, 'app.publish(path)' simulates a request.
  >>> list(root.keys())
  [u'mycollector']

You can use this debug shell to introspect Python objects stored in
ZODB.  You can add, update or delete objects and attributes from the
debug shell.

A default view for collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you try to access the collector from the URL:
http://localhost:8080/mycollector , you will get ``NotFound`` error
like this::

  URL: http://localhost:8080/mycollector
  ...
  NotFound: Object: <tc.collector.ticketcollector.Collector object at 0x9fe44ac>, name: u'@@index'

This error is raised, because there is no view named ``index``
registered for ``ICollector``.  This section will show how to create
a default view for ``ICollector`` interface.

As you have already seen in the :ref:`started-getting` chapter, you
can create a simple view and register it from ZCML.

In the ``src/tc/collector/views.py`` add a new view like this::

  class TicketCollectorMainView(form.DisplayForm):

      def __call__(self):
          return "Hello ticket collector!"

Then, in the ``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ICollector"
     name="index"
     permission="zope.Public"
     class="tc.collector.views.TicketCollectorMainView"
     />

Now you can visit: http://localhost:8080/mycollector
It should display a message like this::

  Hello ticket collector!

In the next section, you will see more details about the main page
for collector.  Also we are going to learn about Zope Page Template.

.. _tut1-main-page:

Creating the main page
----------------------

Browser Page
~~~~~~~~~~~~

The browser page can be created using a page template.  The
``form.DisplayForm`` supports a ``template`` and ``form_fields``
attributes.  You can also remove the ``__call__`` method from
``TicketCollectorMainView``.

::

  from zope.browserpage import ViewPageTemplateFile

  class TicketCollectorMainView(form.DisplayForm):

      form_fields = form.Fields(ICollector)

      template = ViewPageTemplateFile("collectormain.pt")


You can create ``src/tc/collector/collectormain.pt`` with the following
content::

  <html>
  <head>
  <title>Welcome to ticket collector!</title>
  </head>
  <body>

  Welcome to ticket collector!

  </body>
  </html>

Now you can visit: http://localhost:8080/mycollector .  It should
display "Welcome to ticket collector!" message.

.. _tut1-conclusion:

Conclusion
----------

This part of tutorial covered the basics of creating a web
application using BlueBream.  This chapter narrated in detail about
the usage of ``bluebream`` paster project template to create a new
project.  This part of tutorial also walked though the process of
building application using Buildout.  Then, narrated creating an
application container.  Finally, a default view for application
container is also created.  The :ref:`tut2-tutorial` will expand the
application with additional functionalities.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
