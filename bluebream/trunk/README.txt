.. contents:: Table of Contents
   :depth: 2

BlueBream
*********

Introduction
------------

BlueBream makes it easy to setup a new project using Zope packages.
BlueBream generate a project directory from a template called
``bluebream``.  The template is created using `PasteScript
<http://pythonpaste.org/script/developer.html>`_ by Ian Bicking.
Deatailed documentation about BlueBream is available here:
`http://packages.python.org/bluebream
<http://packages.python.org/bluebream>`_

Features
--------

1. Generated project package includes ZTK with few additional
   packages which was part of "Zope 3".

2. Runnable Buildout

3. Functional testing enabled by default using z3c.testsetup

4. Use PasteDeploy to support WSGI based deployment.

5. Create a namespace package by default.

Installation
------------

To create a new project, first you need to install BlueBream::

  $ easy_install bluebream

.. note::

  Access to `PyPI <http://pypi.python.org>`_ is required to perform
  the installation and bootstrapping process.

Once BlueBream is installed, run ``paster`` command to create the
project directory.  The ``create`` sub-command provided by ``paster``
will show a wizard to create the project directory.

::

  $ paster create -t bluebream

You need to provide the project name and namespace package name.  The
project name will be used as the egg name.

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


Usage
-----

The generated package include Buildout's bootstrap.py script and
configuration file.  First you need to bootstrap the buildout::

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
