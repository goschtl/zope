.. contents:: Table of Contents
   :depth: 2

BlueBream
*********

Introduction
------------

`BlueBream <http://bluebream.zope.org>`_ -- formerly known as **Zope
3** -- is a web framework written in the Python programming language.

BlueBream is free/open source software, owned by the `Zope Foundation
<http://foundation.zope.org>`_, licensed under the `Zope Public
License <http://foundation.zope.org/agreements/ZPL_2.1.pdf>`_ (BSD
like, GPL compatible license).

Features
--------

A few features distinguish BlueBream from other Python web
frameworks:

- BlueBream is built on top of the `Zope Tool Kit
  <http://docs.zope.org/zopetoolkit>`_ (ZTK), which has many years of
  experience proving it meets the demanding requirements for stable,
  scalable software.

- BlueBream uses the powerful and familiar Buildout_ system written
  in Python.
  
- BlueBream employs the Zope Object Database ZODB_, a transactional
  object database, providing extremely powerful and easy to use
  persistence.
  
- BlueBream registers components with Zope Component Markup Language
  (`ZCML <http://www.muthukadan.net/docs/zca.html#zcml>`_), an XML
  based configuration language, providing limitless flexibility.

- BlueBream features the `Zope Component Architecture
  <http://muthukadan.net/docs/zca.html>`_ (ZCA) which implements
  *Separation of concerns* to create highly cohesive reusable
  components (zope.component_).

- BlueBream implements Python Web Server Gateway Interface (`WSGI
  <http://www.wsgi.org/wsgi>`_) using `Paste
  <http://pythonpaste.org>`_, `PasteScript
  <http://pythonpaste.org/script>`_, and `PasteDeploy
  <http://pythonpaste.org/deploy>`_.

- BlueBream includes a number of well tested components to implement
  common activities.  A few are of these are:
  
  - zope.publisher_ publishes Python objects on the web, emphasizing
    `WSGI <http://www.wsgi.org/wsgi>`_ compatibility

  - zope.security_ provides a generic mechanism for pluggable 
    security policies

  - zope.testing_ and zope.testbrowser_ offer unit and functional testing 
    frameworks 

  - zope.pagetemplate_ is an XHTML-compliant language for devloping
    templates

  - zope.schema_ is a schema engine

  - zope.formlib_ is a tool for automatically generating forms

.. _Buildout: http://www.buildout.org
.. _ZODB: http://www.zodb.org
.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.publisher: http://pypi.python.org/pypi/zope.publisher
.. _zope.security: http://pypi.python.org/pypi/zope.security
.. _zope.testing: http://pypi.python.org/pypi/zope.testing
.. _zope.testbrowser: http://pypi.python.org/pypi/zope.testbrowser
.. _zope.pagetemplate: http://pypi.python.org/pypi/zope.pagetemplate
.. _zope.schema: http://pypi.python.org/pypi/zope.schema
.. _zope.formlib: http://pypi.python.org/pypi/zope.formlib

Installation
------------

If you have installed `setuptools
<http://pypi.python.org/pypi/setuptools>`_ or `distribute
<http://pypi.python.org/pypi/distribute>`_ an ``easy_install``
command will be available.  Then, you can install BlueBream using
``easy_install`` command like this::

  $ easy_install bluebream

Internet access to `PyPI <http://pypi.python.org/pypi>`_ is required
to perform installation of BlueBream.

The ``bluebream`` distribution provides a template based project
creation based on PasteScript template.  Once BlueBream is installed,
run ``paster`` command to create the project directory structure.
The ``create`` sub-command provided by paster will show a wizard to
create the project directory structure.

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

If you provide an option from the command line, it will not be
prompted by the wizard.  The other variables are give below, you may
be give the values from command line, if required:

- ``interpreter`` -- Name of custom Python interpreter

- ``version`` -- Version (like 0.1)

- ``description`` -- One-line description of the package

- ``long_description`` -- Multi-line description (in reST)

- ``keywords`` -- Space-separated keywords/tags

- ``author`` -- Author name

- ``author_email`` -- Author email

- ``url`` -- URL of homepage

- ``license_name`` -- License name

- ``zip_safe`` -- ``True``, if the package can be distributed as a .zip
  file othewise ``False``.

If you are in a hurry, you can simply press *Enter/Return* key and
change the values later.  But it would be a good idea, if you provide
a good name for your project.

Usage
-----

The generated package is bundled with Buildout configuration and the
Buildout bootstrap script (``bootstrap.py``).  First you need to
bootstrap the buildout itself::

  $ cd sampleproject
  $ python2.6 bootstrap.py

The bootstrap script will install ``zc.buildout`` and ``setuptools``
package.  Also, it will create the basic directory structure.  Next
step is building the application.  To build the application, run the
buildout::

  $ ./bin/buidout

The buildout script will download all dependencies and setup the
environment to run your application.

The most common thing you need while developing application is
running the server.  BlueBream use ``paster`` command provided by
PasteScript to run the WSGI server.  To run the server, you can pass
the PasteDeploy configuration file as the argument to ``serve``
sub-command as given here::

  $ ./bin/paster serve debug.ini

Once you run the server, you can access it here:
http://localhost:8080/ .  The port number (``8080``) can be changed
from the PasteDeploy configuration file (``debug.ini``).

The second most common thing must be running the test cases.
BlueBream by create a testrunner using the ``zc.recipe.testrunner``
Buildout recipe.  You can see a ``test`` command inside the ``bin``
directory.  To run test cases, you can run this command::

  $ ./bin/test

Sometimes you may want to get the debug shell.  BlueBream provides a
Python prompt with your application object.  You can invoke the debug
shell like this::

  $ ./bin/paster shell debug.ini

More about the test runner and debug shell will be exaplained in the
BlueBream Manual.  You can continue reading about BlueBream from the
`documentation site <http://bluebream.zope.org>`_.

Resources
---------

- `Website with documentation <http://bluebream.zope.org>`_

- `Project blog <http://bluebream.posterous.com>`_

- The bugs and issues are tracked at `launchpad
  <https://launchpad.net/bluebream>`_.

- `BlueBream Wiki <http://wiki.zope.org/bluebream>`_

- `PyPI Home <http://pypi.python.org/pypi/bluebream>`_

- `Twitter <http://twitter.com/bluebream>`_

- `Mailing list <https://mail.zope.org/mailman/listinfo/bluebream>`_

- IRC Channel: `#bluebream at irc.freenode.net <http://webchat.freenode.net/?randomnick=1&channels=bluebream>`_

- `Buildbot <http://zope3.afpy.org/buildbot>`_

- The source code is managed at `Zope reposistory
  <http://svn.zope.org/bluebream>`_.  You can perform a read-only
  checkout of trunk code like this (Anonymous access)::

    svn co svn://svn.zope.org/repos/main/bluebream/trunk bluebream

  You can also `become a contributor after signing a contributor
  agreement
  <http://docs.zope.org/developer/becoming-a-contributor.html>`_
