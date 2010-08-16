.. _tut1-tutorial:

Tutorial --- Part 1
===================

.. _tut1-introduction:

Introduction
------------

In the :ref:`started-getting` chapter you learned how to install BlueBream
and create a new project using the ``bluebream`` project template.  In this
tutorial, you will learn how to create a simple ticket collector
application.  This will help you to get more familiar with the concepts of
BlueBream.

Here are the user stories for the ticket collector application:

1. Any number of tickets can be added to one collector.

2. Each new ticket will have a description and one initial
   comment.

3. Additional comments can be added to tickets.

This is the first part of the tutorial.  After completing this chapter, you
should be able to:

- Understand the project directory structure
- Use Buildout and edit Buildout configuration
- Create content objects and interfaces
- Use the form generation tool (zope.formlib)

.. note::

   The examples in this documentation can be downloaded from here:
   http://download.zope.org/bluebream/examples/ticketcollector-1.0.0.tar.bz2

   The source code is available in different stages corresponding to
   sections.

   - Stage 1 : Section 5.2 to 5.7
   - Stage 2 : Section 5.8
   - Stage 3 : Section 5.9
   - Stage 4 : Section 6.2
   - Stage 5 : Section 6.3
   - Stage 6 : Section 6.4 & 6.5
   

.. _tut1-new-project:

Starting a new project
----------------------

Using the *bluebream* project template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this section we will create the directory layout for our ticket collector
application.  I will assume that you have already installed ``bluebream``
using the ``easy_install bluebream`` command as mentioned in the
:ref:`started-getting` chapter.  We are going to use the project name
``ticketcollector`` and the Python package name ``tc.main``.  This will
create a project with egg/distribution name ``ticketcollector``, ``tc`` as a
namespace package and ``main`` as a Python sub-package.  Let's create the
project directory layout for ``ticketcollector``::

  $ paster create -t bluebream

  Selected and implied templates:
    bluebream#bluebream  A BlueBream project, base template

  Enter project name: ticketcollector
  Variables:
    egg:      ticketcollector
    package:  ticketcollector
    project:  ticketcollector
  Enter python_package (Main Python package (with namespace, if any)) ['ticketcollector']: tc.main
  Enter interpreter (Name of custom Python interpreter) ['breampy']:
  Enter bluebream (Which version of BlueBream?
  Check on http://download.zope.org/bluebream/) ['1.0b3']: 
  Enter version (Version (like 0.1)) ['0.1']:
  Enter description (One-line description of the package) ['']: Ticket Collector
  Enter long_description (Multi-line description (in reST)) ['']: An issue tracking application
  Enter keywords (Space-separated keywords/tags) ['']:
  Enter author (Author name) ['']: Baiju M
  Enter author_email (Author email) ['']: baiju@example.com
  Enter url (URL of homepage) ['']:
  Enter license_name (License name) ['']: ZPL
  Creating template bluebream
  Creating directory ./ticketcollector

  Your project has been created! Now, you want to:
  1) put the generated files under version control
  2) run: python boostrap.py
  3) run: ./bin/buildout


As you can see above, we have provided most of the project details.  The
values you provided here may be changed later, however changing the Python
package name may not be as easy as changing other values, because the Python
package name might be referred to in many places in our code later.

Organize the new package
~~~~~~~~~~~~~~~~~~~~~~~~

If you change directory to ``ticketcollector`` you can see a few directories
and files::

  jack@computer:/projects/ticketcollector$ ls -CF
  bootstrap.py  buildout.cfg  debug.ini  deploy.ini  etc/  setup.py  src/  var/

Once the project directory layout is ready you can add it to your version
control system.  You **should not** add the ``src/ticketcollector.egg-info``
directory as it is generated automatically by setuptools.  Here is an
example using `bzr <http://bazaar.canonical.com/en/>`_::

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
recommended step.  You now have a valid source code distribution of your
project that, after building, will produce a running application.  The
project is now completely independent of the ``bluebream`` distribution,
it's only purpose is to help us get to this point.  The project now contains
everything required to install the dependencies from the Internet and to
set-up the application.

Bootstrapping the project
~~~~~~~~~~~~~~~~~~~~~~~~~

The next step is to install Buildout.  The purpose of Buildout is to
automate the building of Python applications from their bare source code
form.  The only basic requirement for Buildout is a Python installation.
BlueBream provides a bootstrapping script to install Buildout and to set up
the project directory for running it.  This bootstrap script is named
``bootstrap.py`` and will do these things:

- Download and install the ``distribute`` distribution from PyPI which
  contains the forked ``setuptools`` Python package inside.

- Download and install the ``zc.buildout`` distribution from PyPI.

- Create the directory structure eg:- bin/ eggs/ parts/ develop-eggs/

- Create a script inside the ``bin`` directory named ``buildout``

When you run ``bootstrap.py`` you can see that it creates a few directories
and the ``bin/buildout`` script as mentioned earlier::

  jack@computer:/projects/ticketcollector$ python bootstrap.py
  Creating directory '/projects/ticketcollector/bin'.
  Creating directory '/projects/ticketcollector/parts'.
  Creating directory '/projects/ticketcollector/develop-eggs'.
  Creating directory '/projects/ticketcollector/eggs'.
  Generated script '/projects/ticketcollector/bin/buildout'.

- The ``bin`` directory is where Buildout installs all the executable
  scripts.

- The ``eggs`` directory is where Buildout installs Python eggs

- The ``parts`` is where Buildout saves all output generated by buildout.
  Buildout expects you to not change anything inside the parts directory as
  it is auto generated by Buildout.

- The ``develop-eggs`` directory is where Buildout saves links to all
  locally developed Python eggs.

Buildout configuration
~~~~~~~~~~~~~~~~~~~~~~

After bootstrapping the project you can build your application.  All the
steps you done so far are only required once per project, but running
buildout is required whenever you make changes to the buildout
configuration.  You are now ready to run ``bin/buildout`` to build the
application, but before doing this, let's have a look at the content of
``buildout.cfg``::

  [buildout]
  develop = .
  extends = http://download.zope.org/bluebream/bluebream-1.0b3.cfg
  parts = app
          test

  [app]
  recipe = zc.recipe.egg
  eggs = ticketcollector
         z3c.evalexception>=2.0
         Paste
         PasteScript
         PasteDeploy
  interpreter = breampy

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector

The buildout configuration file is divided into multiple sections called
*parts*.  The main part is called ``[buildout]``, and it appears as the
first part in the listing above.  Each part will be handled by the Buildout
plugin mechanism, called recipes, except for ``[buildout]``.  ``[buildout]``
is handled as a special case by Buildout since it contains general settings.

Let's look at the main ``[buildout]`` part::

  [buildout]
  develop = .
  extends = http://download.zope.org/bluebream/bluebream-1.0b3.cfg
  parts = app
          test

The first option (``develop``) tells buildout that the current directory is
a Python distribution source, i.e., it contains a ``setup.py`` file.
Buildout will inspect the ``setup.py`` and create a develop egg link inside
the ``develop-eggs`` directory.  The link file should contain the path to
the location where the Python package is residing.  So buildout will make
sure that the packages are always importable.  The value of the ``develop``
option could be a relative path, as given above, or absolute path to some
directory.  You can also add multiple lines to the ``develop`` option with
different paths.

The ``extends`` option tells buildout to include the full content of the
``http://download.zope.org/bluebream/bluebream-1.0b3.cfg`` file as part the
configuration.  You can add multiple lines to the ``extends`` option to
include multiple configuration files.  You can also specify a file in the
local filesystem.

The ``parts`` option lists all the parts to be built by Buildout.  Buildout
expects a recipe for each of the parts listed here.

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
function.  The `zc.recipe.egg <http://pypi.python.org/pypi/zc.recipe.egg>`_
is an advanced Buildout recipe with many features for dealing with eggs.
Most of the dependencies will come as part of the main application egg.  The
option ``eggs`` lists all the eggs.  The first egg, ``ticketcollector`` is
the main locally developed egg.  The last option, ``interpreter`` specifies
the name of the custom interpreter created by this part.  The custom
interpreter contains the paths to all eggs listed here and their
dependencies, so that you can import any module which is listed as a
dependency.

The last part creates the test runner::

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector

The testrunner recipe creates a test runner using the ``zope.testing``
module.  The only mandatory option is ``eggs`` where you can specify the
eggs.

Building the project
~~~~~~~~~~~~~~~~~~~~

Now you can run the ``bin/buildout`` command.  It will take some time to
download all packages from PyPI.  When you run buildout, it will show
something like this::

  jack@computer:/projects/ticketcollector$ ./bin/buildout
  Develop: '/projects/ticketcollector/.'
  Installing app.
  Generated script '/projects/ticketcollector/bin/paster'.
  Generated interpreter '/projects/ticketcollector/bin/breampy'.
  Installing zope_conf.
  Installing test.
  Generated script '/projects/ticketcollector/bin/test'.

In the above example, all eggs are already available in the eggs folder. If
they are not already available, they will be downloaded and installed.  The
buildout also created three more scripts inside the ``bin`` directory.

- The ``paster`` command can be used to run a web server.

- The ``breampy`` command provides a custom Python interpreter with
  all eggs included in its path.

- The ``test`` command can be used to run the test runner.

Now we have a project structure which will allow us to continue developing
our application.

.. _tut1-pastedeploy-configuration:

PasteDeploy configuration
-----------------------------

BlueBream use WSGI to run the server using PasteDeploy.  There are two
PasteDeploy configuration files: one for deployment (``deploy.ini``),
another for development (``debug.ini``).

We will now examine the contents of ``deploy.ini``::

  [app:main]
  use = egg:ticketcollector

  [server:main]
  use = egg:Paste#http
  host = 127.0.0.1
  port = 8080

  [DEFAULT]
  # set the name of the zope.conf file
  zope_conf = %(here)s/etc/zope.conf

First let's look at the ``[app:main]`` section::

  [app:main]
  use = egg:ticketcollector

The ``[app:main]`` section specifies the egg to be used.  PasteDeploy
expects a ``paste.app_factory`` entry point to be defined in the egg.  If
you look at the ``setup.py`` file, you can see that it is defined like
this::

  [paste.app_factory]
  main = tc.main.startup:application_factory

The name of entry point should be ``main``.  Otherwise, it should be
explicitly mentioned in configuration file (``debug.ini`` & ``deploy.ini``).
For example, if the definition is::

  [paste.app_factory]
  testapp = tc.main.startup:application_factory

The PasteDeploy configuration should be changed like this::

  [app:main]
  use = egg:ticketcollector#testapp

The second section (``[server:main]``) specifies the WSGI server::

  [server:main]
  use = egg:Paste#http
  host = 127.0.0.1
  port = 8080

You can change host name, port and the WSGI server itself from this section.
In oder to use any other WSGI server, it should be included in the
dependency list in your Buildoout configuration.

The last section (``[DEFAULT]``) is where you specify default
values::

  [DEFAULT]
  # set the name of the zope.conf file
  zope_conf = %(here)s/etc/zope.conf

The WSGI application defined in ``tc.main.startup`` expects the
``zope_conf`` option defined in the ``[DEFAULT]`` section.  So, this option
is mandatory.  This option specifies the path of the main zope configuration
file. We will look at zope configuration in greater detail in the next
section.

The ``debug.ini`` contains configuration options which are useful for
debugging::

  [loggers]
  keys = root, wsgi

  [handlers]
  keys = console, accesslog

  [formatters]
  keys = generic, accesslog

  [formatter_generic]
  format = %(asctime)s %(levelname)s [%(name)s] %(message)s

  [formatter_accesslog]
  format = %(message)s

  [handler_console]
  class = StreamHandler
  args = (sys.stderr,)
  level = ERROR
  formatter = generic

  [handler_accesslog]
  class = FileHandler
  args = (os.path.join('var', 'log', 'access.log'),
          'a')
  level = INFO
  formatter = accesslog

  [logger_root]
  level = INFO
  handlers = console

  [logger_wsgi]
  level = INFO
  handlers = accesslog
  qualname = wsgi
  propagate = 0

  [filter:translogger]
  use = egg:Paste#translogger
  setup_console_handler = False
  logger_name = wsgi

  [filter-app:main]
  # Change the last part from 'ajax' to 'pdb' for a post-mortem debugger
  # on the console:
  use = egg:z3c.evalexception#ajax
  next = zope

  [app:zope]
  use = egg:ticketcollector
  filter-with = translogger

  [server:main]
  use = egg:Paste#http
  host = 127.0.0.1
  port = 8080

  [DEFAULT]
  # set the name of the debug zope.conf file
  zope_conf = %(here)s/etc/zope-debug.conf

The debug configuration uses ``filter-app`` instead of ``app`` to include
WSGI middlewares.  Currently only one middleware
(``z3c.evalexception#ajax``) is included.  You can look into PastDeploy
documentation for more information about the other sections.  The Zope
configuration file specified here (``etc/zope-debug.conf``) is different
from the deployment configuration.

.. _tut1-zope-configuration:

Zope configuration
------------------

Similar to PasteDeploy configuration, there are two Zope configuration
files: ``etc/zope.conf`` and ``etc/zope-debug.conf``.

This is the content of ``etc/zope.conf``::

  # Identify the component configuration used to define the site:
  site-definition etc/site.zcml

  <zodb>

    <filestorage>
      path var/filestorage/Data.fs
      blob-dir var/blob
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
      path var/log/z3.log
      formatter zope.exceptions.log.Formatter
    </logfile>

    <logfile>
      path STDOUT
      formatter zope.exceptions.log.Formatter
    </logfile>
  </eventlog>

From the ``zope.conf`` file, you can specify the main ZCML file to be loaded
(``site-definition``).  All paths are specified as relative to the top-level
directory where the PasteDeploy configuration file resides.

.. _tut1-site-definition:

The site definition
-------------------

BlueBream use ZCML for application specific configuration.  ZCML is an
XML-based declarative configuration language.  As you have seen already in
``zope.conf`` the main configuration is located at ``etc/site.zcml``.  Here
is the default listing::

  <configure
     xmlns="http://namespaces.zope.org/zope"
     xmlns:browser="http://namespaces.zope.org/browser">

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
    <include package="zope.app.pagetemplate" file="meta.zcml" />
    <include package="zope.app.publisher.xmlrpc" file="meta.zcml" />

    <include package="zope.browserresource" />
    <include package="zope.copypastemove" />
    <include package="zope.publisher" />
    <include package="zope.component" />
    <include package="zope.traversing" />
    <include package="zope.site" />
    <include package="zope.annotation" />
    <include package="zope.principalregistry" />
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
    <include package="zope.session" />
    <include package="zope.error" />
    <include package="zope.app.zcmlfiles" file="menus.zcml" />
    <include package="zope.app.authentication" />
    <include package="zope.app.security.browser" />
    <include package="zope.traversing.browser" />
    <include package="zope.app.pagetemplate" />
    <include package="zope.app.schema" />

    <include package="tc.main" />

  </configure>

The main configuration, ``site.zcml`` contains references to other
configuration files specific to packages.  The ZCML has some directives like
`include``, ``page``, ``defaultView`` etc. available through various
XML-namespaces.  In the ``site.zcml`` the default XML-namespace is
``http://namespaces.zope.org/zope``.  If you look at the top of
``etc/site.zcml``, you can see the XML-namespace refered to like this::

  <configure
   xmlns="http://namespaces.zope.org/zope">

The ``include`` directive is available in
``http://namespaces.zope.org/zope`` namespace.  If you look at other
configuration files you can see some other namespaces, like
``http://namespaces.zope.org/browser``, which contains directives like
``page``.

At the end of ``site.zcml``, project specific configuration files are
included.  For example, the following directive::

  <include package="tc.main" />

will ensure that the file ``src/tc/collector/configure.zcml`` file is
loaded.

You can define common configuration for your entire application in
``site.zcml``.  The content of ``src/tc/collector/configure.zcml`` will look
like this::

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

The file ``securitypolicy.zcml`` is where you can define your security
policies.  As you can see in ``configure.zcml``, it includes ``welcome``.
By default, if you include a package without mentioning the configuration
file, it will include ``configure.zcml``.

.. _tut1-package-meta-data:

Package meta-data
-----------------

BlueBream uses :term:`Distribute` to distribute the application package.
The :term:`Distribute` distribution contains the ``setuptools`` module.

Your ticketcollector package's setup.py will look like this::

  from setuptools import setup, find_packages


  setup(name='ticketcollector',
        version='0.1',
        description='Ticket Collector',
        long_description="""\
  An issue tracking application""",
        # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
        classifiers=[],
        keywords='',
        author='Baiju M',
        author_email='baiju@example.com',
        url='',
        license='ZPL',
        package_dir={'': 'src'},
        packages=find_packages('src'),
        namespace_packages=['tc'],
        include_package_data=True,
        zip_safe=False,
        install_requires=['setuptools',
                          'zope.securitypolicy',
                          'zope.component',
                          'zope.annotation',
                          'zope.browserresource',
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

Most of the details in ``setup.py`` are derived from user input when
creating the project from a template.  In the ``install_requires`` keyword
argument, you can list all dependencies for the package.  There are two
entry points, the first one is used by PasteDeploy to find the WSGI
application factory.  The second entry point registers a sub-command for
``paster`` script named ``shell``.

.. _tut1-running-tests:

Running Tests
-------------

BlueBream use `zope.testing <http://pypi.python.org/pypi/zope.testing>`_ as
the main framework for automated testing.  Along with **zope.testing**, you
can use Python's ``unittest`` and ``doctest`` modules.  Also there is a
functional testing module called `zope.testbrowser
<http://pypi.python.org/pypi/zope.testbrowser>`_ . To set-up the test cases,
layers etc. BlueBream use the `z3c.testsetup
<http://pypi.python.org/pypi/z3c.testsetup>`_ package.

BlueBream use the Buildout recipe called `zc.recipe.testrunner
<http://pypi.python.org/pypi/zc.recipe.testrunner>`_ to generate a test
runner script.

If you look at the buildout configuration, you can see the test runner
part::

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector

The testrunner recipe creates a test runner using the ``zope.testing``
module.  The only mandatory option is ``eggs`` where you can specify the
eggs.

To run all test cases, use the ``bin/test`` command::

  jack@computer:/projects/ticketcollector$ bin/test

This command will find all the test cases and run them.

.. _tut1-app-object:

Creating the application object
-------------------------------

Container objects
~~~~~~~~~~~~~~~~~

In this section we will explore one of the main concepts in BlueBream:
**container objects**.  As mentioned earlier BlueBream uses an object
database called ZODB to store your Python objects.  You can think of an
object database as a container which contains objects; the inner object may
be another container which contains other objects.

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

BlueBream will take care of the persistence of the objects.  In order to
make a custom object persistent the object class will have to inherit from
``persistent.Persistent``.

Some classes in BlueBream that inherit from ``persistent.Persistent``
include:

- ``zope.container.btree.BTreeContainer``
- ``zope.container.folder.Folder``
- ``zope.site.folder.Folder``

When you inherit from any of these classes the instances of that class will
be persistent.  The second thing you need to do to make objects persistent
is to add the object to an existing container object.  You can experiment
with this from the debug shell provided by BlueBream.  But before you try
that out create a container class somewhere in your code which can be
imported later.  You can add this definition to the
``src/tc/collector/__init__.py`` file (Delete it after the experiment)::

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

The name ``root`` refers to the top-level container in the database.  You
can import your own container class, create an instance and add it to the
root folder::

  >>> from tc.main import MyContainer
  >>> root['c1'] = MyContainer()

ZODB is a transactional database so you will have to commit your changes in
order for them to be performed.  To commit your changes use the function
``transaction.commit`` as described below::

  >>> import transaction
  >>> transaction.commit()

Now if you exit the debug prompt and open it again, you will see that you
can access the persistent object::

  $ ./bin/paster shell debug.ini
  ...
  Welcome to the interactive debug prompt.
  The 'root' variable contains the ZODB root folder.
  The 'app' variable contains the Debugger, 'app.publish(path)' simulates a request.
  >>> root['c1']
  <tc.main.MyContainer object at 0x96091ac>

Persisting random objects like this is not a particulary good idea.  The
next section will explain how to create a formal schema for your objects.
Now you can delete the object and remove the ``MyContainer`` class
definition from ``src/tc/collector/__init__.py``.  You can delete the object
like this::

  >>> del(root['c1'])
  >>> import transaction
  >>> transaction.commit()

Declaring an Interface
~~~~~~~~~~~~~~~~~~~~~~

.. note::

   If you have never worked with ``zope.interface`` before, we recommend
   that you read through the :ref:`man-interface` chapter in the manual
   before proceding.

As the first step for creating the main application container object which
is going to hold all other objects, you need to create an interface.  We
will name the main application container interface ``ICollector``.  To make
this interface describe a container object have it inherit
``zope.container.interfaces.IContainer`` or any interface derived from it.
It is recommended to add a site manager inside the main application
container.  In order to add a site manager later, it is recommend to inherit
from ``zope.site.interfaces.IFolder`` interface.  The ``IFolder`` inherits
from ``IContainer``.

To organize project source code in a better way, it is reccomended to use
namespace packages.  You have already created a namespace package named
``tc``.  The ticket collector code can be distributed under different
packages inside ``tc`` namespace.  Let's create a new Python package named
``collector`` inside ``src/tc`` to write the collector related components::

  $ mkdir src/tc/collector
  $ echo "# Python Package" > src/tc/collector/__init__.py

You can now create a file named ``src/tc/collector/interfaces.py`` to add
our interfaces::

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

The interface defined here is your schema for the main application object.
There are two fields defined in the schema.  The first one is ``name`` and
the second one is ``description``.  This schema can later can be used to
auto-generate web forms.

Implementing Interface
~~~~~~~~~~~~~~~~~~~~~~

A schema can be described as a blueprint for your objects as it defines the
fields that the object must implement and the contracts that it must fulfil.
Once written you can create some concrete classes which implement your
schema.

Next, you need to implement this interface.  To implement ``IContainer``,
you can inherit from ``zope.site.folder.Folder``.  You can create the
implementation in ``src/tc/collector/ticketcollector.py``::

  from zope.interface import implements
  from zope.site.folder import Folder

  from tc.collector.interfaces import ICollector

  class Collector(Folder):
      """A simple implementation of a collector using B-Tree
      Container."""

      implements(ICollector)

      name = u""
      description = u""

To declare that a class implements a particular interface you can use the
``implements`` function from ``zope.interface``.

Registering components
~~~~~~~~~~~~~~~~~~~~~~

Once the interfaces and their implementations are ready you can do the
configuration in ZCML.  Open the ``src/tc/collector/configure.zcml`` file
for editing and enter the following to declare ``ICollector`` a content
component::

  <configure
     xmlns="http://namespaces.zope.org/zope"
     xmlns:browser="http://namespaces.zope.org/browser">

    <interface
       interface="tc.collector.interfaces.ICollector"
       type="zope.app.content.interfaces.IContentType"
       />

  </configure>

The ``zope.app.content.interfaces.IContentType`` represents a content type.
If an **interface** provides the ``IContentType`` interface type, then all
objects providing the **interface** are considered to be content objects.

To set annotations for collector objects we need to configure it as
implementing the ``zope.annotation.interfaces.IAttributeAnnotatable``
interface.  The example configuration below also declares that our
``Collector`` class implements
``zope.container.interfaces.IContentContainer``.  These two classes are
examples of marker interfaces, interfaces used to declare that a particular
object belongs to a special type without requiring the presence of any
attributes or methods.

In the same file (``src/tc/collector/configure.zcml``) before the
``</configure>`` add these lines::

  <class class="tc.collector.ticketcollector.Collector">
    <implements
       interface="zope.annotation.interfaces.IAttributeAnnotatable"
       />
    <implements
       interface="zope.container.interfaces.IContentContainer"
       />
    <require
       permission="zope.Public"
       interface="tc.collector.interfaces.ICollector"
       />
    <require
       permission="zope.Public"
       set_schema="tc.collector.interfaces.ICollector"
       />
  </class>

The ``class`` directive is a complex directive.  There are subdirectives
like ``implements`` and ``require`` below the ``class`` directive.  The
``class`` directive listed above also declares permission settings for
``Collector``.

A view for adding collectors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now the content component is ready to use but you will need a web page which
lets us add a ticket collector object.  You can use the ``zope.formlib``
package to create a form view.  You can add the view class definition inside
``src/tc/collector/views.py`` like this::

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

The ``createAndAdd`` function will be called when the user presses the *Add*
button from the web form.  The second last line is very important::

  collector.setSiteManager(LocalSiteManager(collector))

This line adds a site manager to the collector so that it can be used as a
persistent component registry to register local components like local
utilities.

As you have already seen in the previous chapter the ``browser:page``
directive is used for registering pages.  You can use the name
``add_ticket_collector`` and register it for
``zope.site.interfaces.IRootFolder``.  Add these lines to
``src/tc/collector/configure.zcml``::

  <browser:page
     for="zope.site.interfaces.IRootFolder"
     name="add_ticket_collector"
     permission="zope.Public"
     class="tc.collector.views.AddTicketCollector"
     />

The package development is complete now, but it is not yet included from the
main package.  To include this package in the main package (``tc.main``) you
need to modify the ``src/tc/main/configure.zcml`` and add this line before
``</configure>``::

  <include package="tc.collector" />

To add the ticket collector, first you need to login from:
http://localhost:8080/@@login.html .  You can provide the credential
information given in the ``src/tc/main/securitypolicy.zcml``::

  <principal
     id="zope.manager"
     title="Manager"
     login="admin"
     password="admin"
     password_manager="Plain Text"
     />

By default the username & password will be ``admin``, ``admin``.  You
**must** change this to something else.  After successfully logged in, you
can access the URL: http://localhost:8080/@@add_ticket_collector .  It
should display a form where you can enter values for ``name`` and
``description``.  You can enter the ``name`` as ``mycollector``. After
entering your data, submit the form.

You can see that the file size of ``var/filestorage/Data.fs`` increases as
objects are added.  ``Data.fs`` is where the persisted objects are
physically stored.

You can also confirm that the object is actually saved into the database
from the Python shell.  If you go to the Python shell and try to access the
root object you can see that it has the object you added::

  jack@computer:/projects/ticketcollector$ ./bin/paster shell debug.ini
  ...
  Welcome to the interactive debug prompt.
  The 'root' variable contains the ZODB root folder.
  The 'app' variable contains the Debugger, 'app.publish(path)' simulates a request.
  >>> list(root.keys())
  [u'mycollector']

Through this debug shell you can introspect, add, update or delete Python
objects and attributes.

A default view for collector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you try to access the collector from the URL
http://localhost:8080/mycollector you will get a ``NotFound`` error like
this::

  URL: http://localhost:8080/mycollector
  ...
  NotFound: Object: <tc.collector.ticketcollector.Collector object at 0x9fe44ac>, name: u'@@index'

This error is raised because there is no view named ``index`` registered for
``ICollector``.  This section will show you how to create a default view for
the ``ICollector`` interface.

As you have already seen in the :ref:`started-getting` chapter, you can
create a simple view and register it from ZCML.

In ``src/tc/collector/views.py`` add a new view like this::

  class TicketCollectorMainView(form.DisplayForm):

      def __call__(self):
          return "Hello ticket collector!"

Then add the following in ``src/tc/collector/configure.zcml``::

  <browser:page
     for="tc.collector.interfaces.ICollector"
     name="index"
     permission="zope.Public"
     class="tc.collector.views.TicketCollectorMainView"
     />

Now you can visit: http://localhost:8080/mycollector It should display a
message like this::

  Hello ticket collector!

In the next section you will see more details about the main page for
collector.  We're also going to learn about Zope Page Templates.

.. _tut1-main-page:

Creating the main page
----------------------

Browser Page
~~~~~~~~~~~~

The browser page can be created using a page template.  The
``form.DisplayForm`` supports a ``template`` and ``form_fields`` attributes.
You also need to remove the ``__call__`` method from
``TicketCollectorMainView``.  Update the ``TicketCollectorMainView`` class
inside ``src/tc/collector/views.py`` like this::

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

Now you can visit: http://localhost:8080/mycollector .  It should display
"Welcome to ticket collector!".

.. _tut1-conclusions:

Conclusions
-----------

This part of the tutorial covered the basics of creating a web application
using BlueBream.  We have described in detail how to use the ``bluebream``
paster project template to create a new project. We have discussed the
process of building an application using Buildout. We have created an
application container. Finally, a default view for the application container
was created.  :ref:`tut2-tutorial` will expand the application with
additional functionality.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
