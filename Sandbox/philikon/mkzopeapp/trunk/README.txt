With ``mkzopeapp`` you can start a new Zope-based web application from
scratch with just one command::

  $ mkzopeapp MyZopeProj

This will create a directory called ``MyZopeProj``.  In it, you will
find a typical development sandbox for a Python package: a
``setup.py`` file and an empty package called ``myzopeproj`` in which
you can now place the code for your application.  Actually, the
package is not entirely empty, it contains a sample application
configuration (``configure.zcml``) and a sample server configuration
for development (``develop.ini``).

Starting the application
------------------------

In order to start the application, you will have to enable the newly
created package as an egg.  This is best done by activating it as a
*development egg* using the following command::

  $ python2.4 setup.py develop -f http://download.zope.org/distribution

This will not only activate the ``MyZopeProj`` egg, it will also
install all of its dependencies, most importantly the Zope libraries
themselves (that's also why we need to point it to the download
location of Zope libraries).  This might take a little while, by the
way.

Note that both the downloaded eggs as well as the development egg will
be installed into the global ``site-packages`` directory of the
``python2.4`` interpreter you're using.  To avoid that, it is
recommended to use workingenv_ or `zc.buildout`_ to confine the
installation to a local sandbox (see next section).

When ``MyZopeProj`` is enabled as an egg, it installs a new
executable, ``startMyZopeProj``.  This will start the server with the
development configuration (``develop.ini``)::

  $ .../bin/startMyZopeProj

.. _workingenv: http://cheeseshop.python.org/pypi/workingenv.py
.. _zc.buildout: http://cheeseshop.python.org/pypi/zc.buildout

Using workingenv for a sandbox installation
-------------------------------------------

workingenv_ provides an easy way to do egg-based development without
polluting your global Python installation with different versions of
downloaded eggs and development eggs.  Instead, a workingenv-based
sandbox contains its own eggs and (at least by default) ignores any
globally installed eggs.

To turn the ``MyZopeProj`` directory into a workingenv sandbox,
execute::

  $ python workingenv.py MyZopeProj

outside the ``MyZopeProj`` directory.  After that, we only have to
*activate* the sandbox for the current interpreter session::

  $ cd MyZopeProj
  $ . bin/activate

Now we can proceed to activate the ``MyZopeProj`` egg::

  $ python2.4 setup.py develop -f http://download.zope.org/distribution

This is in fact the same line as above, except that it will install
the downloaded dependencies and the ``MyZopeProj`` development egg
into the local sandbox.

After the installation we can find the ``startMyZopeProj`` executable
in the ``bin`` sub-directory of the ``MyZopeProj`` directory.

Using zc.buildout for a sandbox installation
--------------------------------------------

Like workingenv, zc.buildout_ also provides an easy way to work with
eggs in sandboxes without polluting the global Python installation.
An advantage of buildout over workingenv is that we create a
configuration file (``buildout.cfg``) that specifies what we want to
install and then run the buildout command to perform the installation.
That way the sandbox creation with all the dependency installation is
repeatable (e.g. for co-workers).

To turn our ``MyZopeProj`` directory into a buildout sandbox, we add a
``buildout.cfg`` file::

  [buildout]
  develop = .
  find-links = http://download.zope.org/distribution
  parts = app

The first line after the section header tells buildout to call
``setup.py develop`` in the current directory (we no longer have to do
that manually!).  The second line tells it where to find the Zope
dependencies.  Finally, the third line specifies a configuration
section that tells buildout what to install and that we yet have to
write::

  [app]
  recipe = zc.recipe.egg
  eggs = MyZopeProj

The first line after the section header tells buildout that we simply
want to install an egg (buildout has different recipes that can
install anything between an old-fashion Unix tarball to a modern egg).
The second line tells it which egg to install.

Now we need to bootstrap the sandbox and execute the buildout::

  $ buildout bootstrap
  ...
  $ buildout
  ...

This obviously requires that you already have installed
``zc.buildout`` and that the ``buildout`` executable is on your path.

After running the buildout, we can find the ``startMyZopeProj``
executable in the ``bin`` sub-directory of the ``MyZopeProj``
directory.
