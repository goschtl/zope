.. _tut-tutorial:

Tutorial
========

.. _tut-introduction:

Introduction
------------

In the :ref:`started-getting` chapter you learned how to install
BlueBream and create a new project using the ``bluebream`` project
template.  In this chapter, we will explore creating a simple ticket
collector application.  This will help you to familiarize more
concepts in BlueBream.

Before proceeding, we will see the user stories:

1. Individual small ticket collector for each project.  Many
   collectors can be added to one running BlueBream.

2. Any number of tickets can be added to one collector.

3. Each ticket will be added with a description and one initial
   comment.

4. Additional comments can be added to tickets.

.. _tut-new-project:

Starting new project
--------------------

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
  Enter author_email (Author email) ['']: baiju@muthukadan.net
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
  
As you can see above, we have provided most of the project details
and some are skipped.  If you want, it is possible to change the
values provided here later.  But changing the package name or
namespace package name may not be easy as changing the description.
The reason is that, the name and namespace package might be referred
from many places.

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
Python installation and internet access to PyPI.  We will see how
this is becoming possible in the upcoming sections.

The next step is building the application using Buildout.  The
purpose of Buildout is to automate all the process involved in
building an Python application/package from scratch.  The only basic
requirement for Buildout is a Python installation.  Buildout provides
a bootstrapping script to initialize Buildout.  This bootstrap
script named ``bootstrap.py`` will do these things:

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

After bootstrapping the Buildout, you can perform the real building
of your application.  All the steps you have done so far is not
required to be repeated.  But the build step will be required to
repeat whenever you make changed to the buildout configuration.  Now
you are ready to run the ``bin/buildout`` to build the application.
Before running the buildout, let's see the content of
``buildout.cfg``::

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
called parts.  The main part is called ``[buildout]``, and that is
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

Now you can the ``bin/buildout`` command.  This will take some time
to download packages from PyPI.  When you run buildout, it will show
something like this::

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

.. _tut-app-object:

Creating the application object
-------------------------------

You can modify the file named ``src/tc/main/interfaces.py`` to add
new interfaces like this::

  from zope.container.interfaces import IContainer
  from zope.schema import Text

  class ICollector(IContainer):
        """The main application container object."""

        description = Text(
            title=u"Description",
            description=u"A description of the collector.",
            default=u"",
            required=False)

Then implement the interface in ``src/tc/main/ticketcollector.py``::

  from zope.interface import implements
  from zope.container.btree import BTreeContainer

  from tc.main.interfaces import ICollector

  class Collector(BTreeContainer):
      """A simple implementation of a collector using B-Tree
      Container."""

      implements(ICollector)

.. _tut-main-page:

Creating the main page
----------------------

.. _tut-conclusion:

Conclusion
----------

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
