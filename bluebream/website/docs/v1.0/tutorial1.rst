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
collector application.  This will help you to familiarize more
concepts in BlueBream.

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

.. _tut1-new-project:

Starting new project
--------------------

Using project template
~~~~~~~~~~~~~~~~~~~~~~

In this section, we will create the directory layout for ticket
collector application.  I assume you have already installed
``bluebream`` using ``easy_install bluebream`` command as mentioned
in the :ref:`started-getting`.  We are going to use the project name
as ``ticketcollector`` and namespace package as ``tc``. Let's create
the project directory layout for ``ticketcollector``::

  $ paster create -t bluebream
  Selected and implied templates:
    bluebream#bluebream  A Zope project

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
  Enter long_description (Multi-line description (in reST)) ['']: A ticket collector application
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
          Copying README.txt_tmpl to ./ticketcollector/src/tc/main/README.txt
          Copying __init__.py to ./ticketcollector/src/tc/main/__init__.py
          Copying app.py to ./ticketcollector/src/tc/main/app.py
          Copying application.zcml_tmpl to ./ticketcollector/src/tc/main/application.zcml
          Copying configure.zcml_tmpl to ./ticketcollector/src/tc/main/configure.zcml
          Copying debug.py to ./sample/src/test_name/test_main/debug.py
          Copying ftesting.zcml_tmpl to ./ticketcollector/src/tc/main/ftesting.zcml
          Copying interfaces.py to ./ticketcollector/src/tc/main/interfaces.py
          Copying securitypolicy.zcml_tmpl to ./ticketcollector/src/tc/main/securitypolicy.zcml
          Copying startup.py to ./ticketcollector/src/tc/main/startup.py
          Copying tests.py_tmpl to ./ticketcollector/src/tc/main/tests.py
          Copying views.py to ./ticketcollector/src/tc/main/views.py
        Copying __init__.py to ./ticketcollector/src/tc/__init__.py
      Recursing into +package+.egg-info
        Creating ./ticketcollector/src/ticketcollector.egg-info/
        Copying PKG-INFO to ./ticketcollector/src/ticketcollector.egg-info/PKG-INFO
    Recursing into templates
      Creating ./ticketcollector/templates/
      Copying zope_conf.in to ./ticketcollector/templates/zope_conf.in
    Recursing into var
      Creating ./ticketcollector/var/
      Recursing into blob
        Creating ./ticketcollector/var/blob/
        Copying README.txt to ./ticketcollector/var/blob/README.txt
        Recursing into tmp
          Creating ./ticketcollector/var/blob/tmp/
      Recursing into filestorage
        Creating ./ticketcollector/var/filestorage/
        Copying README.txt to ./ticketcollector/var/filestorage/README.txt
      Recursing into log
        Creating ./ticketcollector/var/log/
        Copying README.txt to ./ticketcollector/var/log/README.txt
    Copying versions.cfg to ./ticketcollector/versions.cfg
  Running /opt/baiju/py26/bin/python2.6 setup.py egg_info

As you can see above, we have provided most of the project details.
Later, you can change the values provided here.  However, changing
the package name or namespace package name may not be easy as
changing the description.  Because, the name and namespace package
might be referred from many places.

Organize new package
~~~~~~~~~~~~~~~~~~~~

If you change directory to ``ticketcollector``, you can see few
directories and files::

  jack@computer:/projects/ticketcollector$ ls -CF
  bootstrap.py  debug.ini   etc/      src/        var/
  buildout.cfg  deploy.ini  setup.py  templates/  versions.cfg

Once the project directory layout is ready, you can add it to your
version controlling system.  You need **not** to add
``src/ticketcollector.egg-info`` directory as it is generated by
setuptools.  Here is an example using `bzr
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

Adding source code to version controlling system is an optional step,
but it is recommended even for experiments.  Now you have, a ready to
use, stand alone source code.  You need not to have the ``bluebream``
distribution installed anymore to function any task.  The source code
contains mechanism to install dependencies and setup other things
required.  The only necessary things you need to have is a pure
Python installation and Internet access to PyPI.  We will see how
this is becoming possible in the upcoming sections.

Buildout
~~~~~~~~

The next step is building the application using Buildout.  The
purpose of Buildout is to automate all the process involved in
building any Python application/package from scratch.  The only basic
requirement for Buildout is a Python installation.  Buildout provides
a bootstrapping script to initialize Buildout.  This bootstrap script
named ``bootstrap.py`` will do these things:

- Download and install ``setuptools`` package from PyPI

- Download and install ``zc.buildout`` package from PyPI

- Create directory structure eg:- bin/ eggs/ parts/ develop-eggs/

- Create a script inside ``bin`` directory named ``buildout``

When you run the ``bootstrap.py``, you can see that it creates few
directories and the ``bin/buildout`` script as mentioned earlier::

  jack@computer:/projects/ticketcollector$ python2.6 bootstrap.py
  Creating directory '/projects/ticketcollector/bin'.
  Creating directory '/projects/ticketcollector/parts'.
  Creating directory '/projects/ticketcollector/develop-eggs'.
  Creating directory '/projects/ticketcollector/eggs'.
  Generated script '/projects/ticketcollector/bin/buildout'.

- The ``bin`` directory is where buildout install all the executable
  scripts.

- The ``eggs`` directory is where buildout install Python eggs

- The ``parts`` is where Buildout save all output generated by buildout.
  Buildout expects you to not change anything inside parts directory
  as it is auto generated by Buildout.

- The ``develop-eggs`` directory is where buildout save links to all
  locally developing Python eggs.

Buildout configuration
~~~~~~~~~~~~~~~~~~~~~~

After bootstrapping the Buildout, you can perform the real building
of your application.  All the steps you did so far is not required to
be repeated.  But the build step will be repeated whenever you make
changes to the buildout configuration.  Now you are ready to run the
``bin/buildout`` to build the application.  Before running the
buildout, let's see the content of ``buildout.cfg``::

  [config]
  site_zcml = ${buildout:directory}/etc/site.zcml
  blob = ${buildout:directory}/var/blob
  filestorage = ${buildout:directory}/var/filestorage
  log = ${buildout:directory}/var/log

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
common options referred from other places.  Each part will be handled
by the Buildout plugin mechanism called recipes, with few exceptions.
However, the main part ``[buildout]`` need not to have any recipe,
this part will be handled by Buildout itself.  As you can see above
``[config]`` part also doesn't have any recipe.  So, the ``[config]``
part itself will not be performing any actions.

We will look at each part here.  Let's start with ``[config]``::

  [config]
  site_zcml = ${buildout:directory}/etc/site.zcml
  blob = ${buildout:directory}/var/blob
  filestorage = ${buildout:directory}/var/filestorage
  log = ${buildout:directory}/var/log

The ``[config]`` is kind of meta part which is created for
convenience to hold some common options used by other parts and
templates.  Using ``[config]`` part is a good Buildout pattern used
by many users.  In the above given configuration, the options
provided are _not_ used by other parts directly, but all are used in
one template given in the ``[zope_conf]`` part.  Here is details
about each options:

- ``site_zcml`` -- this is the location where final ``site.zcml``
  file will be residing.  The value of ``${buildout:directory}`` will
  be the absolute path to the directory where you are running
  buildout.  In the above example, the value will be:
  ``/projects/ticketcollector``.  So, the value of ``site_zcml`` will
  be: ``/projects/ticketcollector/etc/site.zcml``

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

The second option ``develop`` says to buildout that, the current
directory is a Python distribution source, i.e., there is a
``setup.py`` file.  Buildout will inspect the ``setup.py`` and add
create develop egg link inside ``develop-eggs`` directory.  The link
file should contain path to location where the Python package is
residing.  So, buildout will make sure that the packages is always
importable.  The value of ``develop`` option could be a relative path
as given above or absolute path to some directory.  You can also add
multiple lines to ``develop`` option with different paths.

The ``extends`` option says buildout to include the full content of
``versions.cfg`` file as part the configuration.  The
``versions.cfg`` is another Buildout configuration file which
contains the release numbers of different dependencies.  You can add
multiple lines to ``extends`` option to include multiple
configuration files.

The ``parts`` option list all the parts to be built by Buildout.
Buildout expects a recipe for each parts listed here.  So, you cannot
include ``config`` part here as it doesn't have any recipe.

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
option, ``interpreter`` specify the name of custom interpreter create
by this part.  The custom interpreter contains path to all eggs
listed here.

The ``zope_conf]`` part creates the ``zope.conf`` from a template::

  [zope_conf]
  recipe = collective.recipe.template
  input = templates/zope_conf.in
  output = etc/zope.conf

This part must be very self explanatory, it creates a ``zope.conf``
file from one template file.  This `collective.recipe.template recipe
<http://pypi.python.org/pypi/collective.recipe.template>`_ is very
popular among Buildout users.  Here is the template file
(``templates/zope_conf.in``)::

  # Identify the component configuration used to define the site:
  site-definition ${config:site_zcml}

  <zodb>
    # Wrap standard FileStorage with BlobStorage proxy to get ZODB blobs
    # support.
    # This won't be needed with ZODB 3.9, as its FileStorage supports
    # blobs by itself. If you use ZODB 3.9, remove the proxy and specify
    # the blob-dir parameter right in in filestorage, just after path.
    <blobstorage>
      blob-dir ${config:blob}
      <filestorage>
        path ${config:filestorage}/Data.fs
      </filestorage>
    </blobstorage>

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

The last part creates test runner::

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector

The testrunner recipe creates test runner using ``zope.testing``
module.  The only mandatory option is ``eggs`` where you can specify
the eggs.

Running Buildout
~~~~~~~~~~~~~~~~

Now you can run the ``bin/buildout`` command.  This will take some
time to download packages from PyPI.  When you run buildout, it will
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
an XML based declarative configuration language.  As you have seen
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

    <include package="tc.main" file="securitypolicy.zcml" />
    <include package="tc.main" file="application.zcml" />

  </configure>

The main configuration, ``site.zcml`` include other configuration
files specific to packages.  The ZCML has some directives like
`include``, ``page``, ``defaultView`` etc. available at various XML
namespaces.  In the ``site.zcml`` the default XML namespace is
``http://namespaces.zope.org/zope``.  If you look at the top of
site.zcml, you can see the namespace defined like this::

  <configure
   xmlns="http://namespaces.zope.org/zope">

The ``include`` directive is available in
``http://namespaces.zope.org/zope`` namespace.  If you look at other
configuration files, you can see some other namespaces like
``http://namespaces.zope.org/browser`` used which has some directives
like ``page``.

At the end of ``site.zcml``, two application specific configuration
files are included like this::

  <include package="tc.main" file="securitypolicy.zcml" />
  <include package="tc.main" file="application.zcml" />

The ``securitypolicy.zcml`` is where you can define the security
policies.  The ``application.zcml`` is a generic configuration file
where you can include other application specific configuration files.
Also you can define common configuration for your entire application.
By default, it will look like this::

  <configure
     i18n_domain="tc.main"
     xmlns="http://namespaces.zope.org/zope"
     xmlns:browser="http://namespaces.zope.org/browser">

    <!-- The following registration (defaultView) register 'index' as
         the default view for a container.  The name of default view
         can be changed to a different value, for example, 'index.html'.
         More details about defaultView registration is available here:
         http://bluebream.zope.org/doc/1.0/howto/defaultview.html
         -->

    <browser:defaultView
       name="index"
       for="zope.container.interfaces.IContainer"
       />

    <include package="tc.main" />

  </configure>

As you can see in the ``application.zcml``, it includes ``tc.main``.
By default, if you include a package without mentioning the
configuration file, it will include ``configure.zcml``.

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
                          'zope.app.twisted',
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

Most of the details in the ``setup.py`` is what you given while
creating the project from template.  In the ``install_requires``
keyword argument, you can list all dependencies for the package.
There are two entry points, the first one is used by PasteDeploy to
find the WSGI application factory.  The second entry point register a
sub-command for ``paster`` script named ``shell`.

Running Tests
-------------

BlueBream use `zope.testing
<http://pypi.python.org/pypi/zope.testing>` as the main framework for
automated testing.  Along with **zope.testing**, you can use Python's
``unittest`` and ``doctest`` modules.  Also there is a functional
testing module called `zope.testbrowser
<http://pypi.python.org/pypi/zope.testbrowser>`_ . To setup the test
cases, layers etc. BlueBream use `z3c.testsetup
<http://pypi.python.org/pypi/z3c.testsetup>` package.

BlueBream use the Buildout recipe called `zc.recipe.testrunner
<http://pypi.python.org/pypi/zc.recipe.testrunner>` to generate test
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

  jack@computer:/projects/ticketcollector$ ./bin/test

This command will find all the test cases and run it.

.. _tut1-app-object:

Creating the application object
-------------------------------

Container objects
~~~~~~~~~~~~~~~~~

In this section, we will explore one of the main concepts in
BlueBream called **container object**.  As mentioned earlier,
BlueBream use an object database called ZODB to store your Python
objects.  You can think of object database as a container which
contains objects, the inner object may be another container which
contains other objects.

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

BlueBream will take care of the persistence of the objects.  To make
one custom object persistent first you need to inheriting from
``persistent.Persistent``.  BlueBream has some classes inheriting
from ``persistent.Persistent``:

- ``zope.container.btree.BTreeContainer``
- ``zope.container.folder.Folder``
- ``zope.site.folder.Folder``

If you inherit from any of these classes, the instance of that class
will be persistent.  The second thing you need to do to make it
persistent is add the object to an existing container object.  You
can experiment this from the debug shell provided by BlueBream.
Before that create a container class somewhere in your code which can
be imported later.  You can add this definition to
``src/tc/main/__init__.py`` file (Delete it after the experiment)::

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

The name, ``root`` referring to the top-level container.  This is the
default location where the object hierarchy starts.  You can import
your own container class and create instance and add it to the root
folder::

  >>> from tc.main import MyContainer
  >>> root['c1'] = MyContainer()

ZODB is transactional database, so you need to commit your
transaction.  To commit transaction, use the ``transaction.commit``
function as given below::

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

Peristing any random objects like this is not a good idea.  The next
section will explain how to create a formal schema for your objects.
Now you can delete the object and remove ``MyContainer`` class
definition from ``src/tc/main/__init__.py``.  You can delete the
object like this::

  >>> del(root['c1'])
  >>> import transaction
  >>> transaction.commit()

Declaring Interface
~~~~~~~~~~~~~~~~~~~

From the overview of introduction chapter, you must be noticed, one
of the important BlueBream feature: BlueBream has transactional
object database (:term:`ZODB`).  This is the reason why relational
database connectivity and ORMs are not discussed yet.  BlueBream
recommend to use the Python based object database called ZODB for
storing data.  BlueBream makes it easy to do this.  In this section,
you will see the basic steps you need to make your objects
persistent.  Having a well defined schema for all objects (data) is a
good idea.

As the first step for creating the main application container object
which is going to hold all other objects, you need to create an
interface.  You can name the main container interface as
``ICollector``, the easiest way to create a container is to inherit
from ``zope.container.interfaces.IContainer`` interface.  You can
modify the file named ``src/tc/main/interfaces.py`` to add new
interfaces like this::

  from zope.container.interfaces import IContainer
  from zope.schema import TextLine
  from zope.schema import Text

  class ICollector(IContainer):
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
``IContainer``, it is recommended to inherit from
``zope.container.btree.BTreeContainer``.  You can create the
implementation in ``src/tc/main/ticketcollector.py``::

  from zope.interface import implements
  from zope.container.btree import BTreeContainer

  from tc.main.interfaces import ICollector

  class Collector(BTreeContainer):
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
the configuration in ZCML.

Mark the ``ICollector`` as a content component::

  <interface
     interface="tc.main.interfaces.ICollector"
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

  <class class="tc.main.ticketcollector.Collector">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <implements
       interface="zope.container.interfaces.IContentContainer"
       />
    <require
       permission="zope.ManageContent"
       interface="tc.main.interfaces.ICollector"
       />
    <require
       permission="zope.ManageContent"
       set_schema="tc.main.interfaces.ICollector"
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
package to create a form::

  from zope.container.interfaces import INameChooser
  from zope.formlib import form

  from tc.main.interfaces import ICollector

  from tc.main.ticketcollector import Collector

  class AddTicketCollector(form.AddForm):

      form_fields = form.Fields(ICollector)

      def createAndAdd(self, data):
          name = data['name']
          description = data.get('description')
          namechooser = INameChooser(self.context)
          collector = Collector()
          collector.name = name
          collector.description = description
          name = namechooser.chooseName(name, collector)
          self.context[name] = collector
          self.request.response.redirect(".")

The ``createAndAdd`` function will be called when used submit *Add*
button from web form.

The last last thing you need to do is registering this view in ZCML.
As you have already seen in the previous chapter, ``browser:page``
directive is used for registering pages.  You can give the name as
``add_ticket_collector`` and register it for
``zope.site.interfaces.IRootFolder``.  Add these lines to
``configure.zcml``::

  <browser:page
     for="zope.site.interfaces.IRootFolder"
     name="add_ticket_collector"
     permission="zope.ManageContent"
     class="tc.main.views.AddTicketCollector"
     />

Now you can access the URL:
http://localhost:8080/@@add_ticket_collector .  It should display a
form where you can enter details like ``name`` and ``description``.
You can enter the ``name`` as ``mycolector``, after entering data,
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
  [u'mycolector']

If you try to access the collector from the URL:
http://localhost:8080/mycolector , you will get ``NotFound`` error
like this::

  URL: http://localhost:8080/mycolector
  ...
  NotFound: Object: <tc.main.ticketcollector.Collector object at 0x9fe44ac>, name: u'@@index'

This error is raised, because there is no view named ``index``
registered for ``ICollector``.  The next section will show how to
create a default view for ``ICollector`` interface.

A default view for collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As you have already seen in the :ref:`started-getting` chapter, you
can create a simple view and register it from ZCML.

In the ``src/tc/main/views.py`` add a new view like this::

  class TicketCollectorMainView(form.DisplayForm):

      def __call__(self):
          return "Hello ticket collector!"

Then, in the ``src/tc/main/configure.zcml``::

  <browser:page
     for="tc.main.interfaces.ICollector"
     name="index"
     permission="zope.Public"
     class="tc.main.views.TicketCollectorMainView"
     />

Now you can visit: http://localhost:8080/mycolector
It should display a message like this:

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


You can create ``src/tc/main/collectormain.pt`` with the following
content::

  <html>
  <head>
  <title>Welcome to ticket collector</title>
  </head>
  <body>

  Welcome to ticket collector

  </body>
  </html>

Now you can visit: http://localhost:8080/mycolector .  It should
display "Welcome to ticket collector" message.

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
