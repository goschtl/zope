Examples
========


.. testsetup::

   import zope.pytest
   import os
   import sys

   zope_pytest_dir = os.path.dirname(zope.pytest.__file__)
   fixture_dir = os.path.join(zope_pytest_dir, 'tests', 'sample_fixtures')

   def register_fixture(name):
       fixture_path = os.path.join(fixture_dir, name)
       sys.path.append(fixture_path)
       return fixture_path

   def unregister_fixture(fixture_path):
       sys.path.remove(fixture_path)
       # Unload all modules in sample_fixtures...
       mod_paths = [(x, getattr(y, '__file__', '')) 
                    for x,y in sys.modules.items()]
       for key, path in mod_paths:
            if not 'sample_fixtures' in path:
                continue
            del sys.modules[key]


Preparing a Package
-------------------

Zope projects often use `zc.buildout` along with `distutils` and
`setuptools` to declare their dependencies from other packages and
create locally executable scripts (including testing scripts). This
step is explained in :ref:`project_setup`.

Here we concentrate on the main Python code, i.e. we leave out the
`setup.py` and `zc.buildout` stuff for a while.

A simple Zope-geared package now could be look like this::

   rootdir
    !
    +--mypkg/
         !
         +---__init__.py
         !
         +---app.py
         !
         +---interfaces.py
         !
         +---ftesting.zcml
         !
         +---configure.zcml
         !
         +---tests/
               !
               +----__init__.py
               !
               +----test_app.py

We prepared several such projects in the sources of :mod:`zope.pytest`
(see ``sample_fixtures/`` in `zope.pytest`s ``tests/``
directory). There we have different versions of a package called
``mypkg`` which we will use here.

.. doctest::
   :hide:

    >>> import os, shutil, sys, tempfile
    >>> import zope.pytest.tests
    >>> fixture = os.path.join(
    ...     os.path.dirname(zope.pytest.tests.__file__), 'mypkg_fixture')
    >>> mypkg_dirtree = os.path.join(fixture, 'mypkg')

The important files contained in the `mypkg` package (beside the real
test modules, changing with each sample) look like this:

`app.py`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/simple/mypkg/app.py

`interfaces.py`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/simple/mypkg/interfaces.py

`configure.zcml`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/simple/mypkg/configure.zcml
     :language: xml

`ftesting.zcml`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/simple/mypkg/ftesting.zcml
     :language: xml


Writing Simple Tests
--------------------

For simple tests we do not need any special setup at all. Instead we
can just put modules starting with ``test_`` into some Python package
and ask pytest to run the tests.

In our package we add the following, pretty plain test file:

`tests/test_app.py`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/simple/mypkg/tests/test_app.py

All tests do the usual plain pytest_ stuff: they are named starting
with ``test_`` so that pytest_ can find them. The second and third
tests check whether the specified interfaces are implemented by the
``SampleApp`` class and instances thereof.

For plain :mod:`zope.interface` related tests we need no special
setup.

.. doctest::
   :hide:

    >>> mypkg_dir = register_fixture('simple')

Then, we run py.test_ with this package as argument:

    >>> import pytest
    >>> pytest.main(mypkg_dir) # doctest: +REPORT_UDIFF
    =============...=== test session starts ====...================
    platform ... -- Python 2... -- pytest-...
    collecting ...
    collected 3 items
    <BLANKLINE>
    .../mypkg/tests/test_app.py ...
    <BLANKLINE>
    =============...=== 3 passed in ... seconds ===...=============
    0

.. doctest::
   :hide:

    >>> unregister_fixture(mypkg_dir)

Excellent! py.test found our tests and executed them.

Apparently we didn't really need `zope.pytest` in this example, as
there was no Zope specific code to test.

Making Use of ZCML
------------------

To make real use of `zope.pytest` we now want to test some ZCML_
registrations we can make in (you guessed it) ZCML_ files.

Imagine our project had a certain utility defined that looks like
this:

`app.py`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/zcml/mypkg/app.py

The `FooUtility` can be registered via ZCML_ like this:

`configure.zcml`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/zcml/mypkg/configure.zcml
     :language: xml

To check whether the `FooUtility` was registered and is available we
first have to configure the Zope Component Architecture
(ZCA). `zope.pytest` here helps with the
:func:`zope.pytest.configure` function. It is normally used inside a
`funcarg`_ function you have to write yourself.

We use this approach in a new test module where we want to test the
`FooUtility`. The new test module is called ``test_foo``.

`tests/test_foo.py`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/zcml/mypkg/tests/test_foo.py

Here the `pytest_funcarg__config` function provides a ``config``
argument for arbitrary test functions you want to write. It can be
deployed by writing test functions that require an argument named
``config`` as shown in the `test_foo_utility` function.

If we had named the ``pytest_funcarg__`` function
``"pytest_funcarg__manfred"``, we had to use an argument called
``manfred`` instead of ``config`` with our test functions.

The configuration used here is based on the local ``ftesting.zcml``
file (which includes ``configure.zcml``). We could easily write
several other funcarg_ functions based on other ZCML files and decide
for each test function, which configuratio we would like to pick for
the respective test, based on the funcarg_ name.

The main point about the shown ``pytest_funcarg__`` function is that
it calls :func:`zope.pytest.configure` which injects setup and
teardown calls into the test that are called automatically
before/after your test. This way the given ZCML files are already
parsed when the `test_foo_utility()` test starts and any registrations
are cleared up afterwards. This is the reason, why the ``foo utility``
looked up in our test can actually be found.

Please note, that in the actual tests we make no use of the passed
`config` parameter. We only request it to inject the necessary setup
and teardown functionality.

.. doctest::
   :hide:

    >>> mypkg_dir = register_fixture('zcml')

When run, all tests pass:

    >>> import pytest
    >>> pytest.main(mypkg_dir)
    =============...=== test session starts ====...================
    platform ... -- Python 2... -- pytest-...
    collecting ...
    collected 5 items
    <BLANKLINE>
    .../mypkg/tests/test_app.py ...
    .../mypkg/tests/test_foo.py ..
    <BLANKLINE>
    =============...=== 5 passed in ... seconds ===...=============
    0

.. doctest::
   :hide:

    >>> unregister_fixture(mypkg_dir)

Both foo tests would fail without `pytest_funcarg__config` preparing
the tests.


Browsing Objects
----------------

The most interesting point about functional testing might be to check
Zope-generated output, i.e. browser pages or similar.

This task needs much more setup where `zope.pytest` can come to help.

.. _ZCML: http://docs.zope.org/zopetoolkit/codingstyle/zcml-style.html
.. _pytest: http://pytest.org/
.. _py.test: http://pytest.org/
.. _funcarg: http://pytest.org/funcargs.html
