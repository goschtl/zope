Getting Started
===============

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

Basic usage
-----------

The generated package include a buildout configuration file and
bootstrap.py.  First you need to bootstrap the buildout itself::

  $ cd sampleproject
  $ python2.6 bootstrap.py

After bootstrap, run the buildout::

  $ ./bin/buidout

To run test cases::

  $ ./bin/test

To run the server::

  $ ./bin/paster serve debug.ini

There is a view named ``hello`` registered by default. which can be
accessed here: http://localhost:8080/@@hello

Package directory structure
---------------------------

::

  myproject/
  |-- bootstrap.py                   
  |-- buildout.cfg        
  |-- debug.ini
  |-- deploy.ini
  |-- etc/
  |   `-- site.zcml
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
  |-- var/
  `-- versions.cfg
