.. contents:: Table of Contents
   :depth: 2

BlueBream
*********

Introduction
------------

`BlueBream <http://bluebream.zope.org>`_ is a web framework written
in Python programming language.  BlueBream is a free/open source
software, owned by the `Zope Foundation
<http://foundation.zope.org>`_, licensed under the `Zope Public
License <http://foundation.zope.org/agreements/ZPL_2.1.pdf>`_ (BSD
like, GPL compatible license).  BlueBream was previously known as
**Zope 3**.

Features
--------

A few of the features which distinguish BlueBream among Python web
frameworks.

- BlueBream is built on top of the `Zope Tool Kit
  <http://docs.zope.org/zopetoolkit>`_ (ZTK), a distillation of
  decades of experience in meeting demanding requirements for stable,
  scalable software.

- BlueBream leverages the power of `Buildout
  <http://www.buildout.org>`_ a build system written in Python.
  
- BlueBream uses the `ZODB <http://pypi.python.org/pypi/ZODB3>`_
  transactional object database, providing extremely powerful and
  easy to use persistence.
  
- BlueBream uses `ZCML
  <http://www.muthukadan.net/docs/zca.html#zcml>`_, an XML based
  configuration language for registering components, providing
  limitless flexibility. If you don't need the power of ZCML and the
  complexity it adds, try `Grok <http://grok.zope.org>`_, which adds
  a layer replacing the declarative configuration of ZCML with
  conventions and declarations in standard Python.

- BlueBream features the `Zope Component Architecture
  <http://muthukadan.net/docs/zca.html>` (ZCA) which implements
  *Separation of concerns* to create highly cohesive reusable
  components (zope.component).

- BlueBream supports `WSGI <http://www.wsgi.org/wsgi>`_ using `Paste
  <http://pythonpaste.org>`_, `PasteScript
  <http://pythonpaste.org/script>`, and `PasteDeploy
  <http://pythonpaste.org/deploy>`.
  
- BlueBream includes a number of compenents which provide well tested
  implementation of common requirements. A few are of these are:
  
  - zope.publisher_ publishes Python objects on the web, it is geared
    towards `WSGI <http://www.wsgi.org/wsgi>` compatibility

  - zope.security_ provides a generic mechanism supporting pluggable 
    security policies

  - zope.testing_ and zope.testbrowser_ offer unit and functional testing 
    frameworks 

  - zope.pagetemplate_ is an XHTML-compliant templating language

  - zope.schema_ and zope.formlib_ provide a schema engine and 
    automatic form generation machinery

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

- ``interpreter`` -- Name of custom Python interpreter

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

If you are in a hurry, you can simply press *Enter/Return* key and
change the values later.  But it would be a good idea, if you provide
good name for your project.

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

To run test cases::

  $ ./bin/test

To get the debug shell::

  $ ./bin/paster shell debug.ini

To run the server::

  $ ./bin/paster serve debug.ini

Now you can access the main page from: http://localhost:8080

You can continue reading about BlueBream from the `documentation site
<http://bluebream.zope.org>`_.

Resources
---------

- The source code is managed at `Zope reposistory
  <http://svn.zope.org/bluebream>`_.  You can checkout the trunk code
  like this (Anonymous access)::

    svn co svn://svn.zope.org/repos/main/bluebream/trunk bluebream

  You can also `become a contributor after signing a contributor
  agreement
  <http://docs.zope.org/developer/becoming-a-contributor.html>`_

- `Project blog <http://bluebream.posterous.com>`_

- The bugs and issues are tracked at `launchpad
  <https://launchpad.net/bluebream>`_.

- `BlueBream Wiki <http://wiki.zope.org/bluebream>`_

- `PyPI Home <http://pypi.python.org/pypi/bluebream>`_

- `Documentation <http://bluebream.zope.org>`_

- `Twitter <http://twitter.com/bluebream>`_

- `Mailing list <https://mail.zope.org/mailman/listinfo/bluebream>`_

- IRC Channel: `#bluebream at irc.freenode.net <http://webchat.freenode.net/?randomnick=1&channels=bluebream>`_

- `Buildbot <http://zope3.afpy.org/buildbot>`_
