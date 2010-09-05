.. _started-getting:

Getting Started
===============

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

- **Preparations:** -- This section discusses about the prerequisites and
  preparations the user needs to start a web application project using
  BlueBream.

- **Installation:** -- It gives the user instructions for installing
  BlueBream.

- **Creating a sample project:** -- This section explains the user how to
  create a sample web application project using the ``bluebream`` project
  template.

- **Building the application:** -- This section explains the user how to
  build the application using Buildout.

- **Basic usage:** -- This section explains the basic usage of the BlueBream
  commands.

- **Package directory structure:** -- This section shows the directory
  structure and describes the purpose of each directory and file.

- At the end, a few hello world examples are also given.


.. _started-preparations:

Requirements
------------

This document assumes that user has already installed Python_ 2.4, 2.5 or
2.6 and Distribute_ (or Setuptools_).  If Distribute (or Setuptools) is
installed, the user will get an ``easy_install`` command which can be used
to install the ``bluebream`` distribution.  Another way of installing
``bluebream`` is by using `PIP`_, a replacement for ``easy_install`` which
is meant to improve on it.  Among advantages, you will be able to uninstall
packages.

The user can also install BlueBream inside an isolated Python environment
created using `Virtualenv`_.  Although, *virtualenv* is not required when
working on the application itself, because `Buildout`_ is available by
default in the application created.  Buildout is the recommended approach to
create repeatable, isolated working environments.  Buildout is a
declarative, configuration-driven build system created by Jim Fulton.

It is recommended to use a custom-built Python for working with BlueBream.
The user is required to install a C compiler (gcc) in his system, and to
have internet access to PyPI_ to perform installation of the ``bluebream``
distribution, to bootstrap the buildout, and to build the application using
Buildout. Internet access is not required for deployment if
`zc.sourcerelease <http://pypi.python.org/pypi/zc.sourcerelease>`_ package
is used.

.. _started-installation:

Installation
------------

If the user has installed Distribute_ (or Setuptools_), an ``easy_install``
command will be available and can be used to install BlueBream.

::

  # easy_install bluebream

or::

  $ sudo easy_install bluebream

Try to avoid running "easy_install" commands as ``root`` or with ``sudo``
for larger installation because it can lead to conflicts with the packaging
system of your OS.  Installing the bluebream template like this is ok,
because it does not pull a lot of dependencies.

As mentioned earlier, Internet access to PyPI_ is required to perform
installation of the ``bluebream`` distribution.  If the user is behind a
proxy, it's up to him to make sure it works.  The ``easy_install`` will look
for the environment variable named ``http_proxy`` on a GNU/Linux platforms.
The user can set it like this::

 $ export http_proxy="http://username:password@PROXY-IP-ADDRESS:PORT"

Apart from the ``bluebream`` distribution, easy_install will download and
install a few dependencies.  The dependencies are:

- PasteScript_
- PasteDeploy_
- Paste_

Installing the ``bluebream`` template package is a one time process.  Once
the project package is ready, the user does not need the ``bluebream``
template package anymore because the package user is about to create will be
self-bootstrappable.

.. _started-sample-project:

Creating a sample project
-------------------------

The ``bluebream`` distribution provides a project template based on
PasteScript_ templates.  Once BlueBream is installed, run the ``paster``
command to create the project directory structure.  The ``create``
sub-command provided by ``paster`` will show a command-line wizard to create
the project directory structure.

::

  $ paster create -t bluebream

This will bring a wizard asking details about the new project.  The user can
choose the package name and version number in the wizard itself.  These
details can also be modified later.  Now, the user gets a working
application with the project name as the name of the egg.  The project name
can be a dotted name, if the user wants his project to be part of a
namespace.  Any number of namespace levels can be used.  The project can be
called 'sample', 'sample.main' or 'sample.app.main' or anything deeper if
necessary.  The subfolder structure will be created accordingly.

Here is a screenshot of sample project creation:

.. image:: images/gettingstarted1.png

The project name and other parameters can be given as a command line
argument::

  $ paster create -t bluebream sampleproject

  $ paster create -t bluebream sampleproject version=0.1

The user does not get asked by the wizard for the options whose values are
already passed through command line.  Other variables can also be given
values from the command line, if required:

- ``python_package`` -- Name of the main Python package (possibly with
  namespaces)

- ``interpreter`` -- Name of the custom Python interpreter

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

   It is recommended to provide the details in the wizard itself but user
   can choose to provide the details at a later stage by simply pressing
   *Enter/Return* key.


.. _started-building:

Building the application
------------------------

As mentioned earlier, the generated package is bundled with a Buildout
configuration (``buildout.cfg``) and a bootstrap script (``bootstrap.py``).
First, the user needs to bootstrap the buildout itself::

  $ cd sampleproject
  $ python bootstrap.py

The bootstrap script will download and install the ``zc.buildout`` and
``distribute`` packages.  Also, it will create the basic directory
structure.

Here is a screenshot of bootstrapping the buildout:

.. image:: images/gettingstarted2.png

The next step is building the application.  To build the application, run
the buildout::

  $ ./bin/buildout

Here is a screenshot of the application being built:

.. image:: images/gettingstarted3.png

The buildout script will download all dependencies and setup the environment
to run your application. This can take some time because many packages are
downloaded. If you don't want these packages to be downloaded again the next
time you create a project, you can set a shared directory in your personal
buildout configuration: create a file ``~/.buildout/default.cfg`` (and the
.buildout folder if needed), with the following contents::

    [buildout]
    newest = false
    unzip = true
    download-cache = /opt/buildout-download-cache

You can choose any value for the ``download-cache``, buildout will create it
for you.

If you set the ``newest = false`` option, buildout will not look for new
version of packages in package server by default.  The ``unzip = true``
makes Buildout to unzip all eggs irrespective of whether it is Zip safe or
not.  The ``download-cache`` is the directory where Buildoout keeps a cached
copy the source eggs downloaded.

The next section will show the basic usage.

.. _started-basic-usage:

Basic usage
-----------

The most common thing a user needs while developing an application is
running the server.  BlueBream uses the ``paster`` command provided by
PasteScript to run the WSGI server.  To run the server, the user can pass
the PasteDeploy configuration file as the argument to the ``serve``
sub-command as given here::

  $ ./bin/paster serve debug.ini

After starting the server, the user can access the site from his browser on
this URL: http://localhost:8080/ .  The port number (``8080``) can be
changed in PasteDeploy configuration file (``debug.ini``) to user choice.

When the user opens the browser, it will look like as shown in this
screenshot:

.. image:: images/gettingstarted4.png

The second most common thing that should be run are the unit tests.
BlueBream creates a testrunner using the ``zc.recipe.testrunner`` Buildout
recipe. The user can see a ``test`` command inside the ``bin`` directory.
To run the test cases, the following command is used::

  $ ./bin/test

Sometimes the user may want to get the debug shell. BlueBream provides a
Python prompt with your application object.  You can invoke the debug shell
in the following way::

  $ ./bin/paster shell debug.ini

More details about the test runner and debug shell are explained in the
BlueBream Manual.

.. _started-directory-structure:

Package directory structure
---------------------------

The default directory structure created by the ``bluebream`` paster project
template is as shown::

    myproject/
    |-- bootstrap.py
    |-- buildout.cfg
    |-- debug.ini
    |-- deploy.ini
    |-- etc
    |   |-- site.zcml
    |   |-- zope.conf
    |   `-- zope-debug.conf
    |-- setup.py
    |-- src
    |   |-- myproject
    |   |   |-- __init__.py
    |   |   |-- configure.zcml
    |   |   |-- debug.py
    |   |   |-- securitypolicy.zcml
    |   |   |-- startup.py
    |   |   |-- tests
    |   |   |   |-- __init__.py
    |   |   |   |-- ftesting.zcml
    |   |   |   `-- tests.py
    |   |   `-- welcome
    |   |       |-- __init__.py
    |   |       |-- app.py
    |   |       |-- configure.zcml
    |   |       |-- ftests.txt
    |   |       |-- index.pt
    |   |       |-- interfaces.py
    |   |       |-- static
    |   |       |   |-- logo.png
    |   |       |   `-- style.css
    |   |       `-- views.py
    |   `-- myproject.egg-info
    |       |-- PKG-INFO
    |       |-- SOURCES.txt
    |       |-- dependency_links.txt
    |       |-- entry_points.txt
    |       |-- not-zip-safe
    |       |-- requires.txt
    |       `-- top_level.txt
    `-- var
        |-- filestorage
        |   `-- README.txt
        `-- log
            `-- README.txt


The name of the top-level directory will always be the project name as given
in the wizard.  The name of the egg will also be the same as the package
name by default. The user can change it to something else from ``setup.py``.
Here are the details about the other files in the project.

Files &  Purpose
~~~~~~~~~~~~~~~~

- ``bootstrap.py`` --  Bootstrap script for Buildout

- ``buildout.cfg`` -- The buildout configuration

- ``debug.ini`` -- The PasteDeploy WSGI configuration for development

- ``deploy.ini`` -- The PasteDeploy WSGI configuration for deployment

- ``etc/`` -- A location to add configuration files

- ``etc/site.zcml`` -- The toplevel ZCML file (from which all others are
  loaded)

- ``etc/zope.conf`` -- The main Zope and ZODB configuration file (Used by
  ``deploy.ini``)

- ``etc/zope-debug.conf`` -- The main Zope and ZODB configuration file (Used
  by ``debug.ini``)

- ``setup.py`` -- Project meta-data to create a distributable archive (a
  distribution)

- ``src/`` -- All the application source code will reside in this directory

- ``src/myproject.egg-info/`` -- This is where all the generated
  distribution related info resides

- ``src/myproject/`` -- This is the main package which contains your
  application code.

- ``src/myproject/configure.zcml`` -- The user can customize this ZCML
  configuration file which is included from ``etc/site.zcml``

- ``src/myproject/debug.py`` -- The debug application object.  The class
  given here will be registered from an entry point.

- ``src/myproject/__init__.py`` -- Boiler plate file to make
  this directory as a Python package.

- ``src/myproject/securitypolicy.zcml`` -- security policy declarations
  which is included from site.zcml

- ``src/myproject/startup.py`` This script is called by the WSGI server to
  start the application. (Mostly boiler plate code)

- ``src/myproject/tests/`` -- The tests package

- ``src/myproject/tests/ftesting.zcml`` -- ZCML configuration for functional
  testing

- ``src/myproject/tests/__init__.py`` -- Boiler plate file to make this
  directory as a Python package.

- ``src/myproject/tests/tests.py`` -- Boiler plate to register
  tests.

- ``src/myproject/welcome/`` -- A sample application.

- ``var/`` -- A place holder directory for storing all database files, log
  files etc.


The next few sections will explain how to create a hello world applications.

.. _started-example-1:

Example 1: Hello World without page template
--------------------------------------------

You can watch the video creating hello world application here:

.. raw:: html

  <object width="480" height="385"><param name="movie"
  value="http://www.youtube.com/v/Onuq2PnFnZ8&hl=en_US&fs=1&rel=0"></param><param
  name="allowFullScreen" value="true"></param><param
  name="allowscriptaccess" value="always"></param><embed
  src="http://www.youtube.com/v/Onuq2PnFnZ8&hl=en_US&fs=1&rel=0"
  type="application/x-shockwave-flash" allowscriptaccess="always"
  allowfullscreen="true" width="480" height="385"></embed></object>

To create a web page which displays ``Hello World!``, you need to create a
view class and register it using the ``browser:page`` ZCML directive.  In
BlueBream, this is called a *Browser Page*.  Sometimes more generic term,
*Browser View* is used instead of *Browser Page* which can be used to refer
to HTTP, XMLRPC, REST and other views.  By default, the page which you are
getting when you access: http://localhost:8080 is a page registered like
this.  You can see the registration inside ``configure.zcml``, the name of
the view will be ``index``.  You can access the default page by explicitly
mentioning the page name in the URL like this:
http://localhost:8080/@@index.  You can refer the :ref:`howto-default-view`
HOWTO for more details about how the default view for a container object is
working.

First you need to create a Python file named ``myhello.py`` at
``src/myproject/myhello.py``::

  $ touch src/myproject/myhello.py

You can define your browser page inside this module.  All browser pages
should implement the ``zope.publisher.interfaces.browser.IBrowserView``
interface.  An easy way to do this would be to inherit from
``zope.publisher.browser.BrowserView`` which is already implementing the
``IBrowserView`` interface.

The content of this file could be like this::

  from zope.publisher.browser import BrowserView

  class HelloView(BrowserView):

      def __call__(self):
          return "Hello World!"

Now you can register this page for a particular interface.  So that it will
be available as a browser page for any object which implement that
particular interface.  Now you can register this for the root folder, which
is implementing ``zope.site.interfaces.IRootFolder`` interface.  So, the
registration will be like this::

  <browser:page
     for="zope.site.interfaces.IRootFolder"
     name="hello"
     permission="zope.Public"
     class=".myhello.HelloView"
     />

Since you are using the ``browser`` XML namespace, you need to advertise it
in the ``configure`` directive::

  <configure
     xmlns="http://namespaces.zope.org/zope"
     xmlns:browser="http://namespaces.zope.org/browser">

You can add this configuration to: ``src/myproject/configure.zcml``.  Now
you can access the view by visiting this URL: http://localhost:8080/@@hello

.. note:: The ``@@`` symbol for view

   ``@@`` is a shortcut for ``++view++``.  (Mnemonically, it kinda looks
   like a pair of goggle-eyes)

   To specify that you want to traverse to a view named ``bar`` of content
   object ``foo``, you could (compactly) say ``.../foo/@@bar`` instead of
   ``.../foo/++view++bar``.

   Note that even the ``@@`` is not necessary if container ``foo`` has no
   element named ``bar`` - it only serves to disambiguate between views of
   an object and things contained within the object.

.. _started-example-2:

Example 2: Hello World with page template
-----------------------------------------

In this example, you will create a hello world using a page template.

Create a page template
~~~~~~~~~~~~~~~~~~~~~~

First you need to create a page template file inside your package.  You can
save it as ``src/myproject/helloworld.pt``, with the following content::

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

This declaration means: there is a web page called `hello2`, available for
any content, rendered by the template helloworld.pt, and this page is
public.  This kind of XML configuration is very common in BlueBream and you
will need it for every page or component.

In the above example, instead of using ``zope.site.interfaces.IRootFolder``
interface, ``*`` is used.  So, this view will be available for all objects.

Restart your application, then visit the following URL:
http://127.0.0.1:8080/@@hello2

.. _started-example-3:

Example 3: A dynamic hello world
--------------------------------

.. based on: http://wiki.zope.org/zope3/ADynamicHelloWorld

This section explain creating a dynamic hello world application.

Python class
~~~~~~~~~~~~

In the ``src/myproject/hello.py`` file, add a few lines of Python code like
this::

  class Hello(object):

      def getText(self):
        name = self.request.get('name')
        if name:
          return "Hello %s !" % name
        else:
          return "Hello ! What's your name ?"

This class defines a browser view in charge of displaying some content.

Page template
~~~~~~~~~~~~~

Now you need a page template to render the page content in HTML. So let's
add a ``hello.pt`` in the ``src/myproject`` directory::

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

The ``tal:content`` directive tells BlueBream to replace the fake content of
the tag with the output of the ``getText`` method of the view class.

ZCML registration
~~~~~~~~~~~~~~~~~

The next step is to associate the view class, the template and the page
name.  This is done with a simple XML configuration language (ZCML).  Edit
the existing file called ``configure.zcml`` and add the following content
before the final ``</configure>``::

  <browser:page name="hello3"
      for="*"
      class=".hello.Hello"
      template="hello.pt"
      permission="zope.Public" />

This declaration means: there is a web page called ``hello3``, available for
any content, managed by the view class ``Hello``, rendered by the template
``hello.pt``, and this page is public.

Since you are using the browser XML namespace, you need to declare it in the
configure directive.  Modify the first lines of the configure.zcml file so
it looks like this (You can skip this step if the browser namespace is
already there from the static hello world view)::

  <configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser">

Restart your application, then visit the following URL:
http://127.0.0.1:8080/@@hello3

You should then see the following text in your browser::

  Hello ! What's your name ?

You can pass a parameter to the Hello view class, by visiting the following
URL: http://127.0.0.1:8080/@@hello3?name=World

You should then see the following text::

  Hello World !

.. _started-conclusion:

Conclusion
----------

This chapter walked through the process of getting started with web
application development with BlueBream.  It also introduced a few simple
``Hello World`` example applications.  The :ref:`tut1-tutorial` chapter will
go through a bigger application to introduce more concepts.


.. _Python: http://www.python.org
.. _Distribute: http://pypi.python.org/pypi/distribute
.. _Setuptools: http://pypi.python.org/pypi/setuptools
.. _PIP: http://pip.openplans.org/
.. _Virtualenv: http://pypi.python.org/pypi/virtualenv
.. _Buildout: http://www.buildout.org
.. _PyPI: http://pypi.python.org/pypi
.. _PasteScript: http://pythonpaste.org/script/developer.html
.. _PasteDeploy: http://pythonpaste.org/deploy/
.. _Paste: http://pythonpaste.org/

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
