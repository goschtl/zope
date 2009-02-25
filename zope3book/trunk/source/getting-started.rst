Getting Started
===============

Introduction
------------

This chapter cover the details of setting up an isolated working
environment for web application development using Python and Zope
components.  As the first step, you will be required to install
Python.  Then, a basic understanding of Buildout, the build system
used to set up development sandbox is required.  More details about
Buildout is given in the next chapter.  Buildout will take care of
download and installion of all the dependency packages.  To create a
project code base, you need to provide the minimal meta-data required
for your project like name, version etc.  These details can be given
in `setup.py` and other configuration details in `buildout.cfg`.


Python installation
-------------------

.. index:: installation

The Zope community has always recommended using a custom built Python
for development and deployment.  Both Python 2.4 and 2.5 should work
for Zope 3.4 KGS packages.  As of now, the author reccomend using
Python 2.5 for any new project.


GNU/Linux
~~~~~~~~~

To install Python, you will be required to install gcc, g++ and other
development tools in your system.  A typical installation of Python
can be done like this:

::

  $ wget -c http://www.python.org/ftp/python/2.5.4/Python-2.5.4.tar.bz2
  $ tar jxvf Python-2.5.4.tar.bz2
  $ cd Python-2.5.4
  $ ./configure --prefix=/home/guest/usr
  $ make
  $ make install

As given above, you can provide an option, ``--prefix`` to install
Python in a particular location.  The above steps install Python
inside ``/home/guest/usr`` directory.

After installation, you can invoke the Python interpreter like this::

  $ ~/usr/bin/python2.5
  >>> print "Hello, world!"
  Hello, world!

.. note::

  If you are not getting old statements in Python interactive prompt
  when using up-arrow key, try installing libreadline development
  libraries (Hint: apt-cache search libreadline).  After installing
  this library, you should install Python again.  You also will be
  required to install zlib (Hint: apt-cache search zlib compression
  library) to properly install Zope 3.


MS Windows
~~~~~~~~~~

Python provide binaries for MS Windows.  You can use the MSI
installer package from python.org


Buildout
--------

.. index:: buildout

Introduction
~~~~~~~~~~~~

We are going to use a build tool called Buildout for developing Zope
3 applications from multiple parts.  Buildout will give you an
isolated working environment for developing applications.  The
Buildout package, named `zc.buildout` is available for download from
PyPI.  This section briefly goes through the usage of Buildout for
developing applications.

Buildout has a `boostrap.py` script for initializing a buildout based
project for development or deployment.  It will download and install
`zc.buildout`, `setuptools` and other dependency modules in a
specified directory.  Once bootstrapped it will create a buildout
executable script inside `bin` directory at the top of your project
source.  The default configuration for each project is `buildout.cfg`
file at the top of your project source.  Whenever you run the
buildout command it will look into the default configuration file and
will do actions based on it.  Normally, the configuration file and
boostrap script will be bundled with the project source itself.
Other than the default configuration file along with the project
source, you may also create a system wide default configuration file
at `~/.buildout/default.cfg` .

Buildout creator Jim Fulton recommend a custom built clean Python
installation, i.e., there should not be any Python modules installed
in your site-packages (ideally, a fresh Python installation).  When you
boostrap your project using Buildout's boostrap.py script, it will
download and install all necessary packages in a specified directory.
So, for an ideal project you only required a custom built clean Python
and the project source with proper Buildout configuration and
bootstrap script along with the source package.


Buildout configuration
~~~~~~~~~~~~~~~~~~~~~~

These days, most of the Python packages are available in egg_ format.
Buildout will download and install the eggs in a specified directory
and the location can be changed from the configuration file.  It is
better to give a system-wide location for eggs directory.  And this
configuration can be added to your system-wide configuration file.
The default configuration file for Buildout is
`~/.buildout/default.cfg` .  We are going to use `eggs` directory
inside your home directory to keep all eggs, so first create those
directories and global configuration file::

  $ cd $HOME
  $ mkdir .buildout
  $ mkdir eggs
  $ touch .buildout/default.cfg

You can add the following to your global configuration file
(`~/.buildout/default.cfg`)::

  [buildout]
  newest = false
  eggs-directory = /home/guest/eggs
  find-links = http://download.zope.org/ppix

The `eggs-directory` is where Buildout stores the eggs that are
downloaded.  The last option, `find-links` points to a reliable
mirror of the Python Package Index (PyPI).  The default
configurations given above will be available to all buildouts in your
system.

.. _egg: http://peak.telecommunity.com/DevCenter/PythonEggs


Setting up development sandbox
------------------------------

.. index:: sandbox

To demonstrate the concepts, tools and techniques, we are going to
develop a ticket collector application.  The application can be used
for issue/bug tracking.  To begin the work, first create a directory
for the project.  After creating the directory, create a
configuration file, `buildout.cfg` as given below.  To bootstrap this
application checkout bootstrap.py and run it using a clean Python.

::

  $ mkdir ticketcollector
  $ cd ticketcollector
  $ echo "#Buildout configuration" > buildout.cfg
  $ svn co svn://svn.zope.org/repos/main/zc.buildout/trunk/bootstrap
  $ ~/usr/bin/python2.4 bootstrap/bootstrap.py

You can see a `buildout` script created inside `bin` directory.  Now
onwards, run this `buildout` script whenever you are changing
Buildout configuration.

.. note::

  You can save `bootstrap.py` in a local repository.  If you are
  using svn for managing repository, create an `svn:external` to the
  svn URL given above.

Our application is basically a Python package.  First, we will create
an `src` directory to place our package.  Inside the `src` directory,
you can create `ticketcollector` Python package.  You can create the
`src` and the `ticketcollector` package like this::

  $ mkdir src
  $ mkdir src/ticketcollector
  $ echo "#Python package" > src/ticketcollector/__init__.py

To start building our package you have to create a `setup.py` file.
The `setup.py` should have the minimum details as given below::

  from setuptools import setup, find_packages

  setup(
      name='ticketcollector',
      version='0.1',

      packages=find_packages('src'),
      package_dir={'': 'src'},

      install_requires=['setuptools',
                        'zope.app.zcmlfiles',
                        'zope.app.twisted',
                        'zope.app.securitypolicy',
                        ],
      include_package_data=True,
      zip_safe=False,
      )

We have included the bare minimum packages required for installation
in `install_requires` argument: `zope.app.zcmlfiles`,
`zope.app.twisted` , `zope.app.securitypolicy` and `setuptools`.

To make this package buildout aware, we have to modify the
`buildout.cfg` as given below::

  [buildout]
  develop = .
  parts = py
  extends = http://download.zope.org/zope3.4/3.4.0/versions.cfg
  versions = versions

  [py]
  recipe = zc.recipe.egg
  eggs = ticketcollector
  interpreter = python

Now run the `buildout` script inside `bin` directory.  It will
download all eggs and install it inside `~/eggs` directory.

::

  $ ./bin/buildout

As you can see above, installing Zope is nothing but just setting up
a buildout with `setup.py` with proper packages given as
`install_requires` in it.

.. note::

  Unless you specify a parts section which use `ticketcollector` in some
  way, Buildout will not download dependency packages.  In the above
  example, we created a `[py]` section with `zc.recipe.egg` recipe.


A simple application
--------------------


Configuring application
~~~~~~~~~~~~~~~~~~~~~~~

We are going to continue the ticketcollector application in this
section.  To run the bare minimum Zope 3, we have to create Zope
Configuration Markup Language (ZCML) file and extend the
`buildout.cfg` with appropriate Buildout recipes.  We are going to
use `zc.zope3recipes:app`, `zc.zope3recipes:instance` and
`zc.recipe.filestorage` recipes for setting up our application.  Here
is our modified buildout.cfg (inside the ticketcollector project
directory)::

  [buildout]
  develop = .
  parts = ticketcollectorapp instance

  [zope3]
  location =

  [ticketcollectorapp]
  recipe = zc.zope3recipes:app
  site.zcml =
    <include
      package="ticketcollector"
      file="application.zcml"
      />
  eggs = ticketcollector

  [instance]
  recipe = zc.zope3recipes:instance
  application = ticketcollectorapp
  zope.conf = ${database:zconfig}

  [database]
  recipe = zc.recipe.filestorage

Then, we will create `application.zcml` inside `src/ticketcollector`
directory with the following text.  Consider it as boiler plate code
now, we will explain this in detail later::

  <configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser"
    >

    <include package="zope.securitypolicy"
      file="meta.zcml"
      />

    <include package="zope.app.zcmlfiles" />
    <include package="zope.app.authentication" />
    <include package="zope.app.securitypolicy" />
    <include package="zope.app.twisted" />

    <securityPolicy
      component="zope.securitypolicy.zopepolicy.ZopeSecurityPolicy"
      />

    <role id="zope.Anonymous" title="Everybody"
      description="All users have this role implicitly"
      />

    <role id="zope.Manager" title="Site Manager" />

    <role id="zope.Member" title="Site Member" />

    <grant permission="zope.View"
      role="zope.Anonymous"
      />

    <grant permission="zope.app.dublincore.view"
      role="zope.Anonymous"
      />

    <grantAll role="zope.Manager" />

    <unauthenticatedPrincipal
      id="zope.anybody"
      title="Unauthenticated User"
      />

    <unauthenticatedGroup
      id="zope.Anybody"
      title="Unauthenticated Users"
      />

    <authenticatedGroup
      id="zope.Authenticated"
      title="Authenticated Users"
      />

    <everybodyGroup
      id="zope.Everybody"
      title="All Users"
      />

    <principal
      id="zope.manager"
      title="Manager"
      login="admin"
      password_manager="Plain Text"
      password="admin"
      />

    <grant
      role="zope.Manager"
      principal="zope.manager"
      />

  </configure>


Running application
~~~~~~~~~~~~~~~~~~~

Now you can run the application by executing `./bin/buildout` command
followed by `./bin/instance` command as given below::

  $ ./bin/buildout
  $ ./bin/instance fg


Using ZMI
~~~~~~~~~

.. index:: ZMI

After running your instance, If you open a web browser and go to
`http://localhost:8080 <http://localhost:8080>`_ you'll see the ZMI
(Zope Management Interface ).

Go ahead and click the `Login` link at the upper right corner.  Enter
the user name and password as admin, which is given in
`applications.zcml`.  Now click on `[top]` under Navigation on the
right.  Play around with adding some content objects (the Zope 3 name
for instances that are visible in the ZMI).  Note how content objects
can be arranged in a hierarchy by adding folders which are special
content objects that can hold other content objects.

There is nothing special about the ZMI, it is just the default skin
for Zope 3.  You can modify it to your liking, or replace it
entirely.

When you're done exploring with the ZMI, go back to the window where
you typed `./bin/instance fg` and press Control-C to stop Zope 3.


Hello world
~~~~~~~~~~~

Now you can begin your development inside `src/ticketcollector`
directory.  Create a `browser.py` with following content::

  from zope.publisher.browser import BrowserView

  class HelloView(BrowserView):

      def __call__(self):
          return """
          <html>
          <head>
            <title>Hello World</title>
          </head>
          <body>
            Hello World
          </body>
          </html>
          """

Now append the following text just above the last line of
application.zcml::

  <browser:page
    for="*"
    name="hello"
    permission="zope.Public"
    class="ticketcollector.browser.HelloView"
    />

After restarting Zope, open `http://localhost:8080/hello
<http://localhost:8080/hello>`_, you can see that it displays `Hello
World!`.


Summary
-------

Setting up a Zope 3 project sandbox is nothing but creating a proper
Buildout configuration which use various Buildout recipes.
