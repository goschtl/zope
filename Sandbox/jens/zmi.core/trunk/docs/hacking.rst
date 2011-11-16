Hacking on :mod:`zmi.core`
==========================


Getting the Code
-----------------

The main repository for :mod:`zmi.core` is in the Zope Subversion
repository:

http://svn.zope.org/zmi.core

You can get a read-only Subversion checkout from there:

.. code-block:: sh

   $ svn checkout svn://svn.zope.org/repos/main/zmi.core/trunk zmi.core


Running the tests in a ``virtualenv``
-------------------------------------

If you use the ``virtualenv`` package to create lightweight Python
development environments, you can run the tests using nothing more
than the ``python`` binary in a virtualenv.  First, create a scratch
environment:

.. code-block:: sh

   $ /path/to/virtualenv --no-site-packages /tmp/hack-zmi.core

Next, get this package registered as a "development egg" in the
environment:

.. code-block:: sh

   $ /tmp/hack-zmi.core/bin/python setup.py develop

Finally, run the tests using the build-in ``setuptools`` testrunner:

.. code-block:: sh

   $ /tmp/hack-zmi.core/bin/python setup.py test
   running test
   ...
   test_empty (zmi.core.tests.Test_notify) ... ok
   test_not_empty (zmi.core.tests.Test_notify) ... ok

   ----------------------------------------------------------------------
   Ran 2 tests in 0.000s

   OK

If you have the :mod:`nose` package installed in the virtualenv, you can
use its testrunner too:

.. code-block:: sh

   $ /tmp/hack-zmi.core/bin/easy_install nose
   ...
   $ /tmp/hack-zmi.core/bin/python setup.py nosetests
   running nosetests
   ...
   ----------------------------------------------------------------------
   Ran 3 tests in 0.011s

   OK

or:

.. code-block:: sh

   $ /tmp/hack-zmi.core/bin/nosetests
   ...
   ----------------------------------------------------------------------
   Ran 3 tests in 0.011s

   OK

If you have the :mod:`coverage` pacakge installed in the virtualenv,
you can see how well the tests cover the code:

.. code-block:: sh

   $ /tmp/hack-zmi.core/bin/easy_install nose coverage
   ...
   $ /tmp/hack-zmi.core/bin/python setup.py nosetests \
       --with coverage --cover-package=zmi.core
   running nosetests
   ...
   Name         Stmts   Exec  Cover   Missing
   ------------------------------------------
   zmi.core       5      5   100%   
   ----------------------------------------------------------------------
   Ran 3 tests in 0.019s

   OK


Building the documentation in a ``virtualenv``
----------------------------------------------

:mod:`zmi.core` uses the nifty :mod:`Sphinx` documentation system
for building its docs.  Using the same virtualenv you set up to run the
tests, you can build the docs:

.. code-block:: sh

   $ /tmp/hack-zmi.core/bin/easy_install Sphinx
   ...
   $ cd docs
   $ PATH=/tmp/hack-zmi.core/bin:$PATH make html
   sphinx-build -b html -d _build/doctrees   . _build/html
   ...
   build succeeded.

   Build finished. The HTML pages are in _build/html.


Running the tests using  :mod:`zc.buildout`
-------------------------------------------

:mod:`zmi.core` ships with its own :file:`buildout.cfg` file and
:file:`bootstrap.py` for setting up a development buildout:

.. code-block:: sh

   $ /path/to/python2.6 bootstrap.py
   ...
   Generated script '.../bin/buildout'
   $ bin/buildout
   Develop: '/home/tseaver/projects/Zope/BTK/event/.'
   ...
   Generated script '.../bin/sphinx-quickstart'.
   Generated script '.../bin/sphinx-build'.

You can now run the tests:

.. code-block:: sh

   $ bin/test --all
   Running zope.testing.testrunner.layer.UnitTests tests:
     Set up zope.testing.testrunner.layer.UnitTests in 0.000 seconds.
     Ran 2 tests with 0 failures and 0 errors in 0.000 seconds.
   Tearing down left over layers:
     Tear down zope.testing.testrunner.layer.UnitTests in 0.000 seconds.


Building the documentation using :mod:`zc.buildout`
---------------------------------------------------

The :mod:`zmi.core` buildout installs the Sphinx scripts required to build
the documentation:

.. code-block:: sh

   $ ./bin/docs
   .../bin/sphinx-build -b html -d .../docs/_build/doctrees   .../docs .../docs/_build/html
   ...
   build succeeded.

   Build finished. The HTML pages are in .../docs/_build/html.


Submitting a Bug Report
-----------------------

:mod:`zmi.core` tracks its bugs on Launchpad:

https://bugs.launchpad.net/zmi.core

Please submit bug reports and feature requests there.


Sharing Your Changes
--------------------

.. note::

   Please ensure that all tests are passing before you submit your code.
   If possible, your submission should include new tests for new features
   or bug fixes, although it is possible that you may have tested your
   new code by updating existing tests.

If you got a read-only checkout from the Subversion repository, and you
have made a change you would like to share, the best route is to let
Subversion help you make a patch file:

.. code-block:: sh

   $ svn diff > zmi.core-cool_feature.patch

You can then upload that patch file as an attachment to a Launchpad bug
report.

