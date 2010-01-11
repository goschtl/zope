Tutorial
========


Introduction
------------

In the `Getting Started <gettingstarted.html>`_ chapater you learned
how to install BlueBream and create a new project using the
``bluebream`` project template.  In this chapter, we will explore
creating a simple ticket collector application.  This will help you
to familiarize more concepts in BlueBream.

Befire proceeding, we will see the user stories:

 1. Individual small ticket collector for each project.  Many
    collectors can be added to one running BlueBream.

 2. Any number of tickets can be added to one collector.

 3. Each ticket will be added with a description and one initial
    comment.

 4. Additional comments can be added to tickets.


Starting new project
--------------------

In this section, we will create the directory layout for ticket
collector application.  I assume you have already installed
``bluebream`` using ``easy_install bluebream`` command as mentioned
in the `Getting Started <gettingstarted.html>`_.  We are going to use
the project name as ``ticketcollector`` and namespace package as
``tc``. Let's create the project directory layout for
``ticketcollector``::

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
          Copying application.zcml_tmpl to ./ticketcollector/src/tc/main/application.zcml
          Copying configure.zcml_tmpl to ./ticketcollector/src/tc/main/configure.zcml
          Copying ftesting.zcml_tmpl to ./ticketcollector/src/tc/main/ftesting.zcml
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
and some are simply skipped.  You can change the values provided here
later, if you desired later.  But changing the package name or
namespace package name may not be as simple as changing the
description as it is referred from many places.

If you change directory to ``ticketcollector``, you can see few
directories and files::

  jack@computer:/projects/ticketcollector$ ls -CF
  bootstrap.py  debug.ini   etc/      src/        var/
  buildout.cfg  deploy.ini  setup.py  templates/  versions.cfg

Once the project directory layout is ready, you can add it to your
version controlling system::

  jack@computer:/projects/ticketcollector$ bzr init
  Created a standalone tree (format: 2a)

You need **not** to add ``src/ticketcollector.egg-info`` directory as
it is generted by setuptools.  After adding code to version
controlling system, you need to bootstrap the Buildout and run
``buildout`` command to build the application.  The purpose of
Buildout is to automate all the process involved in bulding an Python
application/package from scratch.  The only basic requirement for
Buildout is a Python installation.  Buildout provides a bootstrapping
script to to initialize Buildout.  This bootstrap script named
``bootstrap.py`` will do these things:

- Download and install ``setuptools`` package from PyPI

- Download and install ``zc.buildout`` package fron PyPI

- Create directory struture eg:- bin/ eggs/ parts/ develop-eggs/

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
  as it is autogenerated by Buildout.

- The ``develop-eggs`` directory is where buildout save links to all
  locally develping Python eggs.

Now you are ready to run the ``bin/buildout`` to build the
application.  Before running the buildout, let's see the content of
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

.. FIXME: Need to explain the configuration here.

When you run buildout, it will show something like this::

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

- The ``paster`` command can be used to run webserver.

- The ``breampy`` command provides a custom Python interpreter with
  all eggs included in path.

- The ``test`` command can be used to run the test runner.

Creating the application object
-------------------------------

You can create a file named ``src/tc/main/interfaces.py`` to add
interfaces::

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


Creating the main page
----------------------

Conclusion
----------

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
