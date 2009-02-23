Development Tools
=================

Before going to the details about how to develop a web application
using Python and Zope components, we should familiarize some
essential tools like Python eggs, setuptools and buildouts.  If you
are already familiar with these you may skip this chapter.


Eggs and setuptools
-------------------

Eggs_ are Python's new distribution format.  We can make Python
packages in Egg format using setuptool package.  To install an egg,
you can use easy_install_.  An easy way to automate the installtion
would be to use `easy_setup.py` program.  To install setuptool, these
two steps are enough::

  $ wget -c http://peak.telecommunity.com/dist/ez_setup.py
  $ python easy_setup.py


.. _Eggs: http://peak.telecommunity.com/DevCenter/PythonEggs
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall

Buildout
--------

The Buildout project provides support for creating applications,
especially Python applications.  It provides tools for assembling
applications from multiple parts, Python or otherwise.  An
application may actually contain multiple programs, processes, and
configuration settings.

The word `buildout` refers to a description of a set of parts and the
software to create and assemble them.  It is often used informally to
refer to an installed system based on a buildout definition.  For
example, if we are creating an application named `Foo``, then `the
Foo buildout` is the collection of configuration and
application-specific software that allows an instance of the
application to be created.  We may refer to such an instance of the
application informally as `a Foo buildout`.

Buildout provides support for creating, assembling and deploying
applications, especially Python applications.  You can build
applications using Buildout recipes.  Recipes are Python programs
which follows a pattern to build various parts of an application.
For example, a recipe will install Python eggs and another one will
install test runner etc.  Applications can be assembled from multiple
parts with different configurations.  A part can be a Python egg or
any other program.  We have already seen how to use buildout to setup
a Zope~3 application in the getting started chapter.

Buildout recipes
----------------

Buildout recipes are distributed in egg formats.  Some examples of
recipes are:

* zc.recipe.egg -- The egg recipe installes one or more eggs, with
  their dependencies. It installs their console-script entry points
  with the needed eggs included in their paths.

* zc.recipe.testrunner -- The testrunner recipe creates a test runner
  script for one or more eggs.

* zc.recipe.zope3recipes -- Recipes for creating Zope 3 instances
  with distinguishing features:

  - Don't use a skeleton

  - Separates application and instance definition

  - Don't support package-includes


* zc.recipe.filestorage -- The filestorage recipe sets up a ZODB file
  storage for use in a Zope 3 instance creayed by the `zope3recipes`
  recipe.


Using a recipe
~~~~~~~~~~~~~~

The procedure for using a recipe is common for almost all recipes.
You can create buildouts with parts controlled recipes.  Suppose you
want to experiment with one package, say, `zope.component`, you can
use `zc.recipe.egg` for installing it in buildout.  The
`zc.recipe.egg` will also provide an interpreter with the egg
installed in the path.  First you can create a directory and
initialize Buildout:

::

  $ mkdir explore-zope.component
  $ cd explore-zope.component
  $ echo "#Buildout configuration" > buildout.cfg
  $ svn co svn://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap
  $ ~/usr/bin/python2.4 bootstrap/bootstrap.py

Now modify the buildout.cfg like this::

  [buildout]
  parts = py

  [py]
  recipe = zc.recipe.egg
  interpreter = mypython
  eggs = zope.component

Now run `buildout` script inside `bin` directory.  This will download
zope.component and its dependency eggs and install it.  Now you can
access the interpreter created by the Buildout recipe like this::

  $ ./bin/buildout
  $ ./bin/mypython
  >>> import zope.component


Developing a package
--------------------

The initial steps are not different from the above exmaple::

  $ mkdir hello
  $ cd hello
  $ echo "#Buildout configuration" > buildout.cfg
  $ svn co svn://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap
  $ ~/usr/bin/python2.4 bootstrap/bootstrap.py

Our application is a simple hello world package.  First we will
create an `src` directory to place our package.  Inside the `src`
directory, you can create the `hello` Python package.  You can create
the `src` and the `hello` package like this::

  $ mkdir src
  $ mkdir src/hello
  $ echo "#Python package" > src/hello/__init__.py


Now create a file named `say.py` inside the `hello` package with this
code::

  def say_hello():
      print "Hello"

To start building our package you have to create a `setup.py` file.
The `setup.py` should have the minimum details as given below::

  from setuptools import setup, find_packages

  setup(
    name='hello',
    version='0.1',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    install_requires=['setuptools',
                      ],
    entry_points = {'console_scripts':
                    ['print_hello = hello.say:say_hello']},
    include_package_data=True,
    zip_safe=False,
    )

Modify `buildout.cfg` as given below::

  [buildout]
  develop = .
  parts = py

  [py]
  recipe = zc.recipe.egg
  scripts = print_hello
  eggs = hello

Now run `buildout` script inside `bin` directory.  Now you
can run the `print_hello` script.

::

  $ ./bin/buildout
  $ ./bin/print_hello
  Hello


Summary
-------

This chapter provided a brief introduction to eggs.  Later we found
how to use buildout tool for developing application.
