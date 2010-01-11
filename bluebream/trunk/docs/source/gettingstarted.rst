Getting Started
===============

Introduction
------------

This chapter narrate the process of creating a new web application
project using BlueBream.  Also it gives few excercises to familiarize
the basic concepts in BlueBream.  We suggest you to try out all the
commands and excercises given here.  Before proceeding, here is an
overview of the sections.

- **Preparations:** -- Prerequisites and preparations you need to
  make to start a new web application project using BlueBream.

- **Installation:** -- An overview of installing BlueBream.

- **Creating a sample project:** -- Explains creating an example
  project using ``bluebream`` project template.

- **Building the application:** -- Shows how to build the application
  using Buildout.

- **Basic usage section:** -- Explains the basic usage of BlueBream
  commands.

- **Package directory structure:** -- Shows the directory structure
  and decribe the purpose of each directories and files.

At the end, few hello world examples are also given.

Preparations
------------

This book assume that you have already installed `Python 2.6
<http://www.python.org>`_ and `setuptools
<http://pypi.python.org/pypi/setuptools>`_.  As an alternative to
setuptools, you can install `distribute
<http://pypi.python.org/pypi/setuptools>`_.  If setuptools or
distribute is installed you will get an ``easy_install`` command
which you can use to install ``bluebream`` distribution.

You can also install BlueBream inside an isolated Python enironment
created by `virtualenv <http://pypi.python.org/pypi/virtualenv>`_.
Although, *virtualenv* is not necessary as we are going to use
`Buildout <http://www.buildout.org>`_ for repeatable, isolated
working environment.  Buildout is a declarative, configuration driven
build system reccommended by BlueBream.

It is reccommended to use a custom built Python for working with
BlueBream.  You will be required to install a C compiler (gcc) in
your system.  Internet access to `PyPI <http://pypi.python.org>`_ is
required to perform installation of ``bluebream`` distribution.
Internet is required for bootstrapping the Buildout and building the
application.

Installation
------------

If you have installed `setuptools
<http://pypi.python.org/pypi/setuptools>`_ or `distribute
<http://pypi.python.org/pypi/setuptools>`_ an ``easy_install``
command will be available.  Then, you can install BlueBream using
``easy_install`` command like this::

  $ easy_install bluebream

As mentioned earlier, Internet access to `PyPI
<http://pypi.python.org>`_ is required to perform installation of
``bluebream`` distribution.  If you use any proxy, make sure it
works.  The ``easy_install`` will look for the enviroment variable
named ``http_proxy`` in GNU/Linux platforms.  You can set it like this::

 $ set http_proxy="http://username:password@PROXY-IP-ADDRESS:PORT"

Apart from ``bluebream`` distribution, easy_install will download and
install its dependencies.  The dependencies are:

- `Sphinx-PyPI-upload <http://pypi.python.org/pypi/Sphinx-PyPI-upload>`_
- `PasteScript <http://pypi.python.org/pypi/PasteScript>`_
- `PasteDeploy <http://pypi.python.org/pypi/PasteDeploy>`_
- `Paste <http://pypi.python.org/pypi/Paste>`_

Creating a sample project
-------------------------

The ``bluebream`` package provides a template based project creation
script based on `PasteScript
<http://pythonpaste.org/script/developer.html>`_.  Once BlueBream is
installed, run ``paster`` command to create the project directory
structure.  The ``create`` sub-command provided by ``paster`` will
show a wizard to create the project directory structure.

::

  $ paster create -t bluebream

This will bring a wizard asking details about your new project.  If
you provide package name, namespace package name and version number,
you will get a working application which can be modified further.
The project name will be used as the name of egg.  You can also
change the values provided later.

The project name can be give given as a command line argument::

  $ paster create -t bluebream sampleproject

The name of namespace package also can be given from the command line::

  $ paster create -t bluebream sampleproject namespace_package=mycompany

The other variables which can be given from command line are:

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
  .zip file othewise ``False``.

If you are in a hurry, you can simply press *Enter/Return* key and
change the values later.  But it would be a good idea, if you provide
good name for your project.

Building the application
------------------------

The generated package include a buildout configuration file and
``bootstrap.py``.  First you need to bootstrap the buildout itself::

  $ cd sampleproject
  $ python2.6 bootstrap.py

After bootstrap, run the buildout::

  $ ./bin/buildout

Basic usage
-----------

To run test cases::

  $ ./bin/test

To run the server::

  $ ./bin/paster serve debug.ini

The server can be accessed at http://localhost:8080/ now.

Package directory structure
---------------------------

The default directory structure created by the ``bluebream`` paster
project template will look like this::

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
  |           |-- application.zcml
  |           |-- configure.zcml
  |           |-- ftesting.zcml
  |           |-- __init__.py
  |           |-- README.txt
  |           |-- securitypolicy.zcml
  |           |-- startup.py
  |           |-- tests.py
  |           `-- views.py
  |-- templates/
  |   `-- zope_conf.in
  |-- var/
  `-- versions.cfg
  
The name of toplevel directory will be always what you gave as
project name in the wizard.  The name of egg also will be same as
that of package name by default.  But if you want, you can change it
to something else from ``setup.py``.  Here are the details about
other files inside the project.

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

- ``src/mynamespace/main/application.zcml`` -- Boiler plate ZCML to
  include other application specific ZCMLs.  Now only the main
  package is included, you can add other ZCMLs from here.

- ``src/mynamespace/main/configure.zcml`` -- You can customize this
  ZCML which is included from application.zcml


- ``src/mynamespace/main/ftesting.zcml`` -- ZCML for functional
  testing

- ``src/mynamespace/main/__init__.py`` -- The main package

- ``src/mynamespace/main/README.txt`` -- main packages's readme

- ``src/mynamespace/main/securitypolicy.zcml`` -- security policy
  declarations which is included from site.zcml

- ``src/mynamespace/main/startup.py`` This script is called by WSGI
  server to start the application. (Mostly boiler plate code)

- ``src/mynamespace/main/tests.py`` -- Boiler plate to register
  tests.

- ``src/mynamespace/main/views.py`` -- An example view.


- ``templates/`` -- Buildout specific templates used by
  "collective.recipe.template"

- ``templates/zope_conf.in`` -- Zope conf template, modify this file
  for any change in zope.conf

- ``var/`` -- A place holder directory for storing all ZODB files,
  log files etc.

- ``versions.cfg`` -- All versions of files can be pinned down here.


The next few sections will explain how to create hello world
applications.

Example 1: Hello World without page template
--------------------------------------------

To create a page which displays ``Hello World!``, you need to create
a view and then register it using ``browser:page`` ZCML directive.

First you need to create a Python file named ``myhello.py`` at
``src/mynamespace/main/myhello.py``::

  $ touch src/mynamespace/main/myhello.py

You can define your browser view inside this module.  All browser
views should implement
``zope.publisher.interfaces.browser.IBrowserView`` interface.  An
easy way to do this would be to inherit from
``zope.publisher.browser.BrowserView`` which is already implementing
the ``IBrowserView`` interface.

The content of this file could be like this::

  from zope.publisher.browser import BrowserView

  class HelloView(BrowserView):

      def __call__(self):
          return "Hello World!"

Now you can register this view for a particular interface.  So that
it will be available as a browser view for any object which implement
this.  At this point you can register this for root folder which is
implementing ``zope.site.interfaces.IRootFolder`` interface.

So the registration could be like this::

  <browser:page
     for="zope.site.interfaces.IRootFolder"
     name="hello"
     permission="zope.Public"
     class=".myhello.HelloView"
     />

Since we are using the ``browser`` XML namespace, we need to
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

Example 2: Hello World with page template
-----------------------------------------

In this example, we will use a hello world using a page template. 

Create a page template
~~~~~~~~~~~~~~~~~~~~~~

First you need to create a page template file inside your pacakge.
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
If you feel extremely uncomfortable with XML, you should try `Grok
<http://grok.zope.org>`_, which adds a layer on top of ZTK, replacing
declarative configuration with conventions and declarations in
Python.

In the above example, instead of using
``zope.site.interfaces.IRootFolder`` interface, we used ``*``.  So,
this view will be available for all content objects.

Restart your application, then visit the following URL:
http://127.0.0.1:8080/@@hello2

Example 3: A dynamic hello world
--------------------------------

.. based on: http://wiki.zope.org/zope3/ADynamicHelloWorld

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

We now need a page template to render the page content in html. So
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
of the tag with the output of the getText method of the view
class.

ZCML registration
~~~~~~~~~~~~~~~~~

The next step is to associate the view class, the template and the
page name.  This is done with a simple XML configuration language
(ZCML).  Edit the existing file called ``configure.zcml`` and add the
following content before the final ``</configure>``::

  <browser:page name="hello.html"
      for="*"
      class=".hello.Hello"
      template="hello.pt"
      permission="zope.Public" />

This declaration means: there is a web page called ``hello.html``,
available for any content, managed by the view class ``Hello``,
rendered by the template ``hello.pt``, and this page is public.

Since we are using the browser XML namespace, we need to declare it
in the configure directive.  Modify the first lines of the
configure.zcml file so it looks like this (You can skip this step if
the browser namespace is already there from the static hello world
view)::

  <configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser">

Restart your application, then visit the following URL:
http://127.0.0.1:8080/@@hello.html

You should then see the following text in your browser::

  Hello ! What's your name ?

You can pass a parameter to the Hello view class, by visiting the
following URL: http://127.0.0.1:8080/@@hello.html?name=World

You should then see the following text::

  Hello World !

Conclusion
----------

This chapter walked through the process of getting started with web
application development with BlueBream.  Also introduced few simple
``Hello World`` example applications.  The `tutorial
<tutorial.html>`_ chapter will go through a bigger application to
introduce more concepts.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
