kgs.test
========

This script create a test environment for each Zope/Grok package
including those files:

- ``kgs.cfg``: Buildout configuration to test latest released Zope and
  Grok packages.

- ``trunk.cfg``: Buildout configuration to test trunk version of Zope and
  Grok pacakges.

- ``Makefile``: To run all the test with ``make``.

It will checkout the trunk of each package in the working
directory.

Configuration
-------------

You can set those environment variable:

- ``PYTHON_CACHE_EGG``: Where your cache egg is.

- ``ZOPE3_SVN``: Url to the Zope SVN. By default it's
  ``svn://svn.zope.org/repos/main/``. You might want to change it to
  include your username, or use a mirror.

Running
-------

After having run that script, you can create/edit a ``buildout.cfg``,
which extend either ``kgs.cfg`` or ``trunk.cfg``. You can add to
``develop`` the current egg your are working on.

After running that buildout, you will find a test script for each
package in your ``bin`` directory.
