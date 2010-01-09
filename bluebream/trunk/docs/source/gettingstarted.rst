Getting Started
===============

Introduction
------------

This chapter walks through the process involved in creating a new
project using BlueBream.  The Preparations section gives you an idea
about what are the preparation you need to make to proceed with the
further steps.  The Installation section gives an overview of
installing a BlueBream.  "Creating a sample project" section explains
creating an example project using ``bluebream`` project template.
The next section shows how to build the application.  Basic usage
section explains the basic usage of project.  The "Package directory
structure" shows the directory structure and decribe each directories
and files purpose.  "Hello World" sections shows how to create a
hello page.

Preparations
------------

This book assume that you have already installed `Python 2.6
<http://www.python.org>`_ and `setuptools
<http://pypi.python.org/pypi/setuptools>`_/`distribute
<http://pypi.python.org/pypi/setuptools>`_ package.  It is
reccommended to use a custom built Python for working with BlueBream.
You will be required to install a C compiler (gcc) in your system.
Access to `PyPI <http://pypi.python.org>`_ is required to perform the
installation and bootstrapping process.

Installation
------------

If you have installed `setuptools
<http://pypi.python.org/pypi/setuptools>`_/`distribute
<http://pypi.python.org/pypi/setuptools>`_ an ``easy_install``
command will be available.  You can install BlueBream using
``easy_install`` command like this::

  $ easy_install bluebream

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

- version: Version (like 0.1)

- description: One-line description of the package

- long_description: Multi-line description (in reST)

- keywords: Space-separated keywords/tags

- author: Author name

- author_email: Author email

- url: URL of homepage

- license_name: License name

- zip_safe: ``True``, if the package can be distributed as a .zip
  file othewise ``False``.

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

The default directory structure created by the "bluebream" paster
template will looks like this::

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
to something else from "setup.py".  Here are the details about other
files inside the project.

+-------------------------------------------+--------------------------------------------------+
| Directories & Files                       | Purpose                                          |
+===========================================+==================================================+
| bootstrap.py                              | Bootstrap script for Buildout                    |
+-------------------------------------------+--------------------------------------------------+
| buildout.cfg                              | The buildout configuration                       |
+-------------------------------------------+--------------------------------------------------+
| debug.ini                                 | The PasteDeploy configuration for development    |
+-------------------------------------------+--------------------------------------------------+
| deploy.ini                                | The PasteDeploy configuration for deployment     |
+-------------------------------------------+--------------------------------------------------+
| etc/                                      | A location to add configuration files            |
+-------------------------------------------+--------------------------------------------------+
| etc/site.zcml                             | The main ZCML file                               |
+-------------------------------------------+--------------------------------------------------+
| etc/zope.conf                             | The main Zope configuration file (generated      |
|                                           | from template)                                   |
+-------------------------------------------+--------------------------------------------------+
| setup.py                                  | Project meta-data for creating distribution      |
+-------------------------------------------+--------------------------------------------------+
| src/                                      | All source code will be residing inside this     |
|                                           | directory                                        |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace.egg-info/                 | This is where all distribution related info      |
|                                           | residing                                         |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/                          | The namespace package                            |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/__init__.py               | This file with default content would be enough   |
|                                           | to make this a namespace package.                |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/                     | This is the main package which contains your     |
|                                           | application code.                                |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/application.zcml     | Boiler plate ZCML to include other application   |
|                                           | specific ZCMLs.  Now only the main package is    |
|                                           | included, you can add other ZCMLs from here.     |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/configure.zcml       | You can customize this ZCML which is included    |
|                                           | from application.zcml                            |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/ftesting.zcml        | ZCML for functional testing                      |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/__init__.py          | The main package                                 |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/README.txt           | main packages's readme                           |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/securitypolicy.zcml  | security policy declarations which is included   |
|                                           | from site.zcml                                   |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/startup.py           | This script is called by WSGI server to start    |
|                                           | the application. (Mostly boiler plate)           |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/tests.py             | Boiler plate to register tests.                  |
+-------------------------------------------+--------------------------------------------------+
| src/mynamespace/main/views.py             | An example view.                                 |
+-------------------------------------------+--------------------------------------------------+
| templates/                                | Buildout specific templates used by              |
|                                           | "collective.recipe.template"                     |
+-------------------------------------------+--------------------------------------------------+
| templates/zope_conf.in                    | Zope conf template, modify this file for any     |
|                                           | change in zope.conf                              |
+-------------------------------------------+--------------------------------------------------+
| var/                                      | A place holder directory for storing all ZODB    |
|                                           | files, log files etc.                            |
+-------------------------------------------+--------------------------------------------------+
| versions.cfg                              | All versions of files can be pinned down here.   |
+-------------------------------------------+--------------------------------------------------+

The next section will explain how to create a hello world view.

Hello World
-----------

To create a page which displays "Hello World", you need to create a
view and then register it using ``browser:page`` ZCML directive.  Add
a Python file named ``myhello.py`` at
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
          return "Hello"

Now you can register this view for a particular interface.  So that
it will be available as a browser view for any object which implement
this.  At this point you can register this for root folder which is
implementing ``zope.site.interfaces.IRootFolder`` interface.

So the registration could be like this::

  <page
     for="zope.site.interfaces.IRootFolder"
     name="hello"
     permission="zope.Public"
     class=".myhello.HelloView"
     />

You can add this to: ``src/mynamespace/main/configure.zcml``.
Run the application and visit: http://localhost:8080/@@hello

Conclusion
----------

This chapter exaplained about getting started with application
development using BlueBream.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
