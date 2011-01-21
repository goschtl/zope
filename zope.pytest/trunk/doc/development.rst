Developing :mod:`zope.pytest`
*****************************

You want to contribute to :mod:`zope.pytest`? Great!

Please talk to us our on our :ref:`mailing list <mailing_list>` about
your plans!

Sources
-------

`zope.pytest` source code is maintained on Zope subversion repository:
http://svn.zope.org/zope.pytest

You can check out `zope.pytest` using `Subversion`_ (SVN).

.. _`Subversion`: http://subversion.tigris.org/

Feel free to checkout `zope.pytest` from Zope repository if you want
to hack on it, and send us a request when you want us to merge
your improvements.

Development install of `zope.pytest`
------------------------------------

`zope.pytest` requires Python 2.5 or 2.6.

To install `zope.pytest` for development, first check it out, then run the
buildout::

 $ python bootstrap.py -d
 $ bin/buildout

This uses Buildout_. Don't worry, that's all you need to know to get
going. The ``-d`` option is to use Distribute_ instead of Setuptools_
and is optional. The buildout process will download and install all
dependencies for `zope.pytest`.

.. _Buildout: http://buildout.org

.. _Distribute: http://packages.python.org/distribute/

.. _Setuptools: http://pypi.python.org/pypi/setuptools

Tests
-----

To run the tests::

  $ bin/py.test

This uses `py.test`_. We love tests, so please write some if you want
to contribute. There are many examples of tests in the ``test_*.py``
modules.

.. _`py.test`: http://pytest.org/

Test coverage
-------------

To get a test coverage report::

  $ bin/py.test --cov zope.pytest

To get a report with more details::

   bin/py.test --cov-report html --cov zope.pytest

The results will be stored in a subdirectory ``htmlcov``. You can point
a web browser to its ``index.html`` to get a detailed coverage report.

Building the documentation
--------------------------

To build the documentation using Sphinx_::

  $ cd doc/
  $ make html

.. _Sphinx: http://sphinx.pocoo.org/

If you use this command, all the dependencies will have been set up
for Sphinx so that the API documentation can be automatically
extracted from the `zope.pytest` source code. The docs source is in
``doc/``, the built documentation will be available in
``doc/_build/html``.

We also have to support for testing the docs. These tests can be run
in the ``doc`` dir as well::

  $ make doctest

Releasers should make sure that all tests pass.


Python with `zope.pytest` on the sys.path
-----------------------------------------

It's often useful to have a project and its dependencies available for
import on a Python prompt for experimentation:

  $ bin/devpython

You can now import `zope.pytest`::

  >>> import zope.pytest

You can also run your own scripts with this custom interpreter if you
like::

  $ bin/devpython somescript.py

This can be useful for quick experimentation. When you want to use
`zope.pytest` in your own projects you would normally include it in
your project's ``setup.py`` dependencies instead.

Releases
--------

The buildout also installs `zest.releaser`_ which can be used to make
automatic releases to PyPI (using ``bin/fullrelease``).

.. _`zest.releaser`: http://pypi.python.org/pypi/zest.releaser
