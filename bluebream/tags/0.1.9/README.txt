.. contents:: Table of Contents
   :depth: 2

BlueBream
*********

Introduction
------------

`BlueBream <http://packages.python.org/bluebream>`_ is a web
framework written in Python programming language.  BlueBream is the
new name for "Zope 3".  This package makes it easy to setup a new
project using BlueBream.  It generates a project directory from a
template called ``bluebream``.  The template is created using
`PasteScript <http://pythonpaste.org/script/developer.html>`_ by Ian
Bicking.

.. raw:: html

  <script src="http://widgets.twimg.com/j/2/widget.js"></script>
  <script> new TWTR.Widget({ version: 2, type: 'search', search:
  'bluebream', interval: 6000, title: 'The Zope Web Framework',
  subject: 'BlueBream', width: 480, height: 300, theme: { shell: {
  background: '#8ec1da', color: '#ffffff' }, tweets: { background:
  '#ffffff', color: '#444444', links: '#1985b5' } }, features: {
  scrollbar: false, loop: true, live: true, hashtags: true,
  timestamp: true, avatars: true, behavior: 'default' }
  }).render().start(); </script> <br/>

.. raw:: html

  <object width="480" height="295"><param name="movie"
  value="http://www.youtube.com/v/HyG5Qee5wbs&hl=en_US&fs=1&">
  </param> <param name="allowFullScreen" value="true"></param><param
  name="allowscriptaccess" value="always"></param><embed
  src="http://www.youtube.com/v/HyG5Qee5wbs&hl=en_US&fs=1&"
  type="application/x-shockwave-flash" allowscriptaccess="always"
  allowfullscreen="true" width="480" height="295"></embed></object>

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

To get the debug shell::

  $ ./bin/paster shell debug.ini

To run the server::

  $ ./bin/paster serve debug.ini

There is a view named ``index`` registered by default for root
folder. which can be accessed here: http://localhost:8080/@@index

You can continue reading about BlueBream from the `documentation site
<http://packages.python.org/bluebream>`_.

Resources
---------

- The source code is managed at `Zope reposistory
  <http://svn.zope.org/bluebream>`_.  You can checkout the trunk code
  like this (Anonymous access)::

    svn co svn://svn.zope.org/repos/main/bluebream/trunk bluebream

  You can also `become a contributor after signing a contributor
  agreement
  <http://docs.zope.org/developer/becoming-a-contributor.html>`_.

- The bugs and issues are tracked at `launchpad
  <https://launchpad.net/bluebream>`_.

- There is also a `Wiki <http://wiki.zope.org/bluebream>`_ available.

- `PyPI page <http://pypi.python.org/pypi/bluebream>`_

- `Documentation <http://packages.python.org/bluebream>`_

- `Twitter <http://twitter.com/bluebream>`_

- `Mailing list <https://mail.zope.org/mailman/listinfo/zope3-users>`_

- IRC Channel: `#bluebream <http://webchat.freenode.net/?randomnick=1&channels=bluebream>`_ at irc.freenode.net
