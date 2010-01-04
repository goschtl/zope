BlueBream
*********

BlueBream makes it easy to setup a new project using Zope packages.
BlueBream generate a project directory from a template called
``bluebream``.  The template is created using `PasteScript
<http://pythonpaste.org/script/developer.html>`_ by Ian Bicking.

To create a new project, first you need to install BlueBream::

  $ easy_install bluebream

.. note::

  Access to `PyPI <http://pypi.python.org>`_ is required to perform
  the installation and bootstrapping process.

Once BlueBream is installed, run ``paster`` command to create the
project directory.  The ``create`` subcommand provided by ``paster``
will show a wizard to create the project directory.

::

  $ paster create -t bluebream

You need to provide the project name and namespace package name.  The
project name will be used as the egg name.

The project name can be give given as a command line argument::

  $ paster create -t bluebream sample

The name of namespace package also can be given from the command line::

  $ paster create -t bluebream sample namespace_package=mycompany
