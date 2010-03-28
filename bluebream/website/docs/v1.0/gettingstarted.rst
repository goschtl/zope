.. _started-getting:

Getting Started
===============

.. warning::

   This documentation is under construction.  See the `Documentation
   Status <http://wiki.zope.org/bluebream/DocumentationStatus>`_ page
   in wiki for the current status and timeline.

.. _started-intro:

Introduction
------------

This chapter narrates you to create a web application project using
BlueBream.  If you complete this chapter, you should be able to:

- Install PasteScript based BlueBream project template

- Create a BlueBream application project using the template

- Bootstrap the build system (Buildout) and build the application

- Run WSGI based web server to serve the application

- Run test cases and use the debug shell

- Create Hello World applications

Before proceeding further, let's have an overview of the sections.

- **Preparations:** -- This section discusses about the prerequisites
  and preparations user need to start a web application project using
  BlueBream.

- **Installation:** -- It gives the user instructions for installing
  BlueBream.

- **Creating a sample project:** -- This section explains the user
  how to create a sample web application project using ``bluebream``
  project template.

- **Building the application:** -- This section explains the user to
  build the application using Buildout.

- **Basic usage:** -- This section explains the basic usage of
  BlueBream commands.

- **Package directory structure:** -- This section shows the
  directory structure and describes the purpose of each directory and
  files.

- At the end, a few hello world examples are also given.


.. _started-preparations:

Preparations
------------

This document assumes that user has already installed `Python 2.6
<http://www.python.org>`_ and `setuptools
<http://pypi.python.org/pypi/setuptools>`_.  As an alternative to
setuptools, user can install `distribute
<http://pypi.python.org/pypi/distribute>`_.  If setuptools or
distribute is installed then user will get an ``easy_install``
command which can be used to install ``bluebream`` distribution.

User can also install BlueBream inside a Python environment created
using `virtualenv <http://pypi.python.org/pypi/virtualenv>`_.
Although, *virtualenv* may not be required when user is working on
the application itself because, `Buildout <http://www.buildout.org>`_
support will be available in the application created.  Buildout is
the recommended approach to create repeatable, isolated working
environments.  Buildout is a declarative, configuration driven build
system created by Jim Fulton.

It is recommended to use a custom built Python for working with
BlueBream.  User required to install a C compiler (gcc) in his
system.  User is required to have internet access to `PyPI
<http://pypi.python.org/pypi>`_ to perform installation of
``bluebream`` distribution, to build the application using Buildout
and to bootstrap the buildout itself.  Internet access is not
required for deployment if `zc.sourcerelease
<http://pypi.python.org/pypi/zc.sourcerelease>`_ package is used.

.. _started-installation:

Installation
------------

If user has installed `setuptools
<http://pypi.python.org/pypi/setuptools>`_ or `distribute
<http://pypi.python.org/pypi/distribute>`_, ``easy_install`` command
will be available and can be used to install BlueBream.

::

  $ easy_install bluebream

As mentioned earlier, Internet access to `PyPI
<http://pypi.python.org/pypi>`_ is required to perform installation
of ``bluebream`` distribution.  If user is using any proxy, its upto
the user to make sure it works.  The ``easy_install`` will look for
the environment variable named ``http_proxy`` in GNU/Linux platforms.
User can set it like this::

 $ export http_proxy="http://username:password@PROXY-IP-ADDRESS:PORT"

Apart from ``bluebream`` distribution, easy_install will download and
install its dependencies.  The dependencies are:

- `PasteScript <http://pypi.python.org/pypi/PasteScript>`_
- `PasteDeploy <http://pypi.python.org/pypi/PasteDeploy>`_
- `Paste <http://pypi.python.org/pypi/Paste>`_

The installation of ``bluebream`` project template package is a one
time process.  Once the project package is ready, user need not
require the ``bluebream`` project template package anymore because
the project package user is going to create will be
self-bootstrappable.

.. _started-sample-project:

Creating a sample project
-------------------------

The ``bluebream`` distribution provides project templates based on
`PasteScript template
<http://pythonpaste.org/script/developer.html>`_.  Once BlueBream is
installed, run ``paster`` command to create the project directory
structure.  The ``create`` sub-command provided by ``paster`` will
show a wizard to create the project directory structure.

::

  $ paster create -t bluebream

This will bring a wizard asking details about the new project.  User
can choose to provide package name, namespace package name and
version number in the wizard itself otherwise these details can also
be modified later.  Now, user gets a working application with project
name as the name of the egg.

Here is a screenshot of sample project creation:

.. image:: images/gettingstarted1.png

The project name as well as namespace package name can be given as a
command line argument::

  $ paster create -t bluebream sampleproject

  $ paster create -t bluebream sampleproject namespace_package=mycompany

User does not get asked by the wizard for the options whose values
are already passed through command line.Other variables can also be
given values from command line, if required:

- ``interpreter`` -- Name of custom Python interpreter

- ``version`` -- Version (like 0.1)

- ``description`` -- One-line description of the package

- ``long_description`` -- Multi-line description (in reST)

- ``keywords`` -- Space-separated keywords/tags

- ``author`` -- Author name

- ``author_email`` -- Author email

- ``url`` -- URL of homepage

- ``license_name`` -- License name

- ``zip_safe`` -- ``True``, if the package can be distributed as a
  .zip file otherwise ``False``.

.. note:: Recommended use of Wizard

   It is recommended to provide the details in the wizard itself but
   user can choose to provide the details at a later stage by simply
   pressing *Enter/Return* key.

.. note:: Alternate Project Templates

   An alternate project template named ``bluebream_simple`` is also
   available, and its `documented in the wiki
   <http://wiki.zope.org/bluebream/AlternateProjectTemplates>`_.

.. _started-building:

Building the application
------------------------

As mentioned earlier, the generated package is bundled with Buildout
configuration (``buildout.cfg``) and Buildout bootstrap script
(``bootstrap.py``).  First, user needs to bootstrap the buildout
itself::

  $ cd sampleproject
  $ python bootstrap.py

The bootstrap script will install ``zc.buildout`` and ``setuptools``
package.  Also, it will create the basic directory structure.

Here is a screenshot of bootstrapping the buildout:

.. image:: images/gettingstarted2.png

Next step is building the application.  To build the application, run
the buildout::

  $ ./bin/buildout

Here is a screenshot of building the application:

.. image:: images/gettingstarted3.png

The buildout script will download all dependencies and setup the
environment to run your application.  The next section will show the
basic usage.

.. _started-basic-usage:

Basic usage
-----------

The most common thing user need while developing application is
running the server.  BlueBream use ``paster`` command provided by
PasteScript to run the WSGI server.  To run the server, user can pass
the PasteDeploy configuration file as the argument to ``serve``
sub-command as given here::

  $ ./bin/paster serve debug.ini

After running the server, user can access the site from browser by
this URL: http://localhost:8080/ .  The port number (``8080``) can be
changed in PasteDeploy configuration file (``debug.ini``) to user
choice.

When user opens the browser, it will look like as shown in this
screenshot:

.. image:: images/gettingstarted4.png

The second most common thing that must be running are the test cases.
BlueBream creates a testrunner using the ``zc.recipe.testrunner``
Buildout recipe.  User can see a ``test`` command inside the ``bin``
directory.  To run test cases, following command is used::

  $ ./bin/test

Sometimes user may want to get the debug shell.  BlueBream provides a
Python prompt with your application object.  You can invoke the debug
shell in the following way::

  $ ./bin/paster shell debug.ini

More details about the test runner and debug shell are explained in
the BlueBream Manual.

.. _started-directory-structure:

Package directory structure
---------------------------

The default directory structure created by the ``bluebream`` paster
project template is as shown::

  myproject/
  |-- bootstrap.py
  |-- buildout.cfg
  |-- debug.ini
  |-- deploy.ini
  |-- etc/
  |   |-- site.zcml
  |   `-- zope.conf
  |-- setup.py
  |-- src/
  |   |-- mynamespace.egg-info/
  |   `-- mynamespace/
  |       |-- __init__.py
  |       `-- main/
  |           |-- configure.zcml
  |           |-- debug.py
  |           |-- __init__.py
  |           |-- securitypolicy.zcml
  |           |-- startup.py
  |           |-- tests/
  |           |   |-- ftesting.zcml
  |           |   |-- __init__.py
  |           |   `-- tests.py
  |           `-- welcome/
  |-- templates/
  |   `-- zope_conf.in
  |-- var/
  `-- versions.cfg
  
The name of top-level directory will always be the project name as
given in the wizard.  The name of egg also will be same as that of
package name by default.  User can change it to something else from
``setup.py``.  Here are the details about other files inside the
project.

Files &  Purpose
~~~~~~~~~~~~~~~~

- ``bootstrap.py`` --  Bootstrap script for Buildout

- ``buildout.cfg`` -- The buildout configuration                      

- ``debug.ini`` -- The PasteDeploy configuration for development

- ``deploy.ini`` -- The PasteDeploy configuration for deployment

- ``etc/`` -- A location to add configuration files            

- ``etc/site.zcml`` -- The main ZCML file                               

- ``etc/zope.conf`` -- The main Zope configuration file (generated
  from template)

- ``setup.py`` -- Project meta-data for creating distribution 

- ``src/`` -- All source code will be residing inside this directory

- ``src/mynamespace.egg-info/`` -- This is where all distribution
  related info residing

- ``src/mynamespace/`` -- The namespace package                            

- ``src/mynamespace/__init__.py`` -- This file with default content
  would be enough to make this a namespace package.

- ``src/mynamespace/main/`` -- This is the main package which
  contains your application code.

- ``src/mynamespace/main/configure.zcml`` -- User can customize this
  ZCML which is included from ``etc/site.zcml``

- ``src/mynamespace/main/debug.py`` -- The debug application object.
  The class given here will be registered from an entry point.

- ``src/mynamespace/main/__init__.py`` -- Boiler plate file to make
  this directory as a Python package.

- ``src/mynamespace/main/securitypolicy.zcml`` -- security policy
  declarations which is included from site.zcml

- ``src/mynamespace/main/startup.py`` This script is called by WSGI
  server to start the application. (Mostly boiler plate code)

- ``src/mynamespace/main/tests/`` -- The tests package

- ``src/mynamespace/main/tests/ftesting.zcml`` -- ZCML for functional
  testing

- ``src/mynamespace/main/tests/__init__.py`` -- Boiler plate file to
  make this directory as a Python package.

- ``src/mynamespace/main/tests/tests.py`` -- Boiler plate to register
  tests.

- ``src/mynamespace/main/welcome/`` -- A sample application.

- ``templates/`` -- Buildout specific templates used by
  "collective.recipe.template"

- ``templates/zope_conf.in`` -- Zope conf template, modify this file
  for any change in zope.conf

- ``var/`` -- A place holder directory for storing all ZODB files,
  log files etc.

- ``versions.cfg`` -- All versions of files can be pinned down here.


The next few sections will explain how to create hello world
applications.

.. _started-example-1:

Example 1: Hello World without page template
--------------------------------------------

You can watch the video creating hello world application here:

.. raw:: html

  <object width="480" height="385"><param name="movie" value="http://www.youtube.com/v/Onuq2PnFnZ8&hl=en_US&fs=1&rel=0"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="http://www.youtube.com/v/Onuq2PnFnZ8&hl=en_US&fs=1&rel=0" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="480" height="385"></embed></object>

To create a web page which displays ``Hello World!``, you need to
create a view class and register it using ``browser:page`` ZCML
directive.  In BlueBream, this is called as *Browser Page*.
Sometimes more generic term, *View* is used instead of *Browser Page*
which can be used to refer to HTTP, XMLRPC, REST and other views.  By
default, the default page which you are getting when you access:
http://localhost:8080 is a page registered like this.  You can see
the registration inside ``configure.zcml``, the name of view will be
``index``.  You can access the default page by explicitly mentioning
the page name in the URL like this: http://localhost:8080/@@index.
You can refer the :ref:`howto-default-view` HOWTO for more details
about how the default view for a container object is working.

First you need to create a Python file named ``myhello.py`` at
``src/mynamespace/main/myhello.py``::

  $ touch src/mynamespace/main/myhello.py

You can define your browser page inside this module.  All browser
pages should implement
``zope.publisher.interfaces.browser.IBrowserView`` interface.  An
easy way to do this would be to inherit from
``zope.publisher.browser.BrowserView`` which is already implementing
the ``IBrowserView`` interface.

The content of this file could be like this::

  from zope.publisher.browser import BrowserView

  class HelloView(BrowserView):

      def __call__(self):
          return "Hello World!"

Now you can register this page for a particular interface.  So that
it will be available as a browser page for any object which implement
that particular interface.  Now you can register this for the root
folder, which is implementing ``zope.site.interfaces.IRootFolder``
interface.  So, the registration will be like this::

  <browser:page
     for="zope.site.interfaces.IRootFolder"
     name="hello"
     permission="zope.Public"
     class=".myhello.HelloView"
     />

Since you are using the ``browser`` XML namespace, you need to
advertise it in the ``configure`` directive::

  <configure
     xmlns="http://namespaces.zope.org/zope"
     xmlns:browser="http://namespaces.zope.org/browser">

You can add this configuration to:
``src/mynamespace/main/configure.zcml``.  Now you can access the view
by visiting this URL: http://localhost:8080/@@hello

.. note:: The ``@@`` symbol for view

   ``@@`` is a shortcut for ``++view++``.
   (Mnemonically, it kinda looks like a pair of goggle-eyes)

   To specify that you want to traverse to a view named ``bar`` of
   content object ``foo``, you could (compactly) say ``.../foo/@@bar``
   instead of ``.../foo/++view++bar``.

   Note that even the ``@@`` is not necessary if container ``foo``
   has no element named ``bar`` - it only serves to disambiguate
   between views of an object and things contained within the object.

.. _started-example-2:

Example 2: Hello World with page template
-----------------------------------------

In this example, you will create a hello world using a page template.

Create a page template
~~~~~~~~~~~~~~~~~~~~~~

First you need to create a page template file inside your package.
You can save it as ``src/mynamespace/main/helloworld.pt``, with the
following content::

  <html>
    <head>
      <title>Hello World!</title>
    </head>
    <body>
      <div>
        Hello World!
      </div>
    </body>
  </html>

Register the page
~~~~~~~~~~~~~~~~~

Update ``configure.zcml`` to add this new page registration.

::

  <browser:page
    name="hello2"
    for="*"
    template="helloworld.pt"
    permission="zope.Public" />

This declaration means: there is a web page called `hello2`,
available for any content, rendered by the template helloworld.pt,
and this page is public.  This kind of XML configuration is very
common in BlueBream and you will need it for every page or component.

In the above example, instead of using
``zope.site.interfaces.IRootFolder`` interface, ``*`` is used.  So,
this view will be available for all objects.

Restart your application, then visit the following URL:
http://127.0.0.1:8080/@@hello2

.. _started-example-3:

Example 3: A dynamic hello world
--------------------------------

.. based on: http://wiki.zope.org/zope3/ADynamicHelloWorld

This section explain creating a dynamic hello world application.

Python class
~~~~~~~~~~~~

In the ``src/mynamespace/main/hello.py`` file, add few lines of
Python code like this::

  class Hello(object):

      def getText(self):
        name = self.request.get('name')
        if name:
          return "Hello %s !" % name
        else:
          return "Hello ! What's your name ?"

This class defines a browser view in charge of displaying some
content.

Page template
~~~~~~~~~~~~~

Now you need a page template to render the page content in html. So
let's add a ``hello.pt`` in the ``src/mynamespace/main`` directory::

  <html>
    <head>
      <title>hello world page</title>
    </head>
    <body>
      <div tal:content="view/getText">
        fake content
      </div>
    </body>
  </html>

The ``tal:content`` directive tells zope to replace the fake content
of the tag with the output of the getText method of the view class.

ZCML registration
~~~~~~~~~~~~~~~~~

The next step is to associate the view class, the template and the
page name.  This is done with a simple XML configuration language
(ZCML).  Edit the existing file called ``configure.zcml`` and add the
following content before the final ``</configure>``::

  <browser:page name="hello3"
      for="*"
      class=".hello.Hello"
      template="hello.pt"
      permission="zope.Public" />

This declaration means: there is a web page called ``hello3``,
available for any content, managed by the view class ``Hello``,
rendered by the template ``hello.pt``, and this page is public.

Since you are using the browser XML namespace, you need to declare it
in the configure directive.  Modify the first lines of the
configure.zcml file so it looks like this (You can skip this step if
the browser namespace is already there from the static hello world
view)::

  <configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser">

Restart your application, then visit the following URL:
http://127.0.0.1:8080/@@hello3

You should then see the following text in your browser::

  Hello ! What's your name ?

You can pass a parameter to the Hello view class, by visiting the
following URL: http://127.0.0.1:8080/@@hello3?name=World

You should then see the following text::

  Hello World !

.. _started-conclusion:

Conclusion
----------

This chapter walked through the process of getting started with web
application development with BlueBream.  Also introduced few simple
``Hello World`` example applications.  The :ref:`tut1-tutorial`
chapter will go through a bigger application to introduce more
concepts.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
