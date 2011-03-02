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
    collecting ...collected 3 items
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

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/zcml/mypkg2/app.py

The `FooUtility` can be registered via ZCML_ like this:

`configure.zcml`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/zcml/mypkg2/configure.zcml
     :language: xml

To check whether the `FooUtility` was registered and is available we
first have to configure the Zope Component Architecture
(ZCA). `zope.pytest` here helps with the
:func:`zope.pytest.configure` function. It is normally used inside a
`funcarg`_ function you have to write yourself.

We use this approach in a new test module where we want to test the
`FooUtility`. The new test module is called ``test_foo``.

`tests/test_foo.py`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/zcml/mypkg2/tests/test_foo.py

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
    collecting ...collected 5 items
    <BLANKLINE>
    .../mypkg2/tests/test_app.py ...
    .../mypkg2/tests/test_foo.py ..
    <BLANKLINE>
    =============...=== 5 passed in ... seconds ===...=============
    0

.. doctest::
   :hide:

    >>> unregister_fixture(mypkg_dir)

Both foo tests would fail without `pytest_funcarg__config` preparing
the tests.


Functional Testing: Browsing Objects
------------------------------------

The most interesting point about functional testing might be to check
Zope-generated output, i.e. browser pages or similar. This is, what
normally is referred to as 'functional testing'.

This task normally needs much more setup where `zope.pytest` can come
to help to minimize the efforts dramatically.

To show this we add a view for the `SampleApp` class we defined in
``app.py`` above. We add a new module ``browser.py`` in our `mypkg`
package with the following contents:

New module `browser.py`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/browser/mypkg3/browser.py

This is a simple browser page that sets the content type of any HTTP
response and returns a simple string as content.

However, to make content browsable we need more registrations. In
``configure.zcml`` we register the main components as above but this
time including also the new browser page:

`configure.zcml`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/browser/mypkg3/configure.zcml
     :language: xml

In ``ftesting.zcml`` we do all the registration stuff that is normally
done in the ``site.zcml``.

`ftesting.zcml`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/browser/mypkg3/ftesting.zcml
     :language: xml

Now we are ready to add another test module that checks the new view
defined in the `browser` module:

`tests/test_browser.py`:

  .. literalinclude:: ../src/zope/pytest/tests/sample_fixtures/browser/mypkg3/tests/test_browser.py

Here we have three tests. While the first one checks only whether the
component architecture can generate the new view in general, with the
latter ones (`test_browser` and `test_infrae_browser`) we access the
whole machinery via a real WSGI application. This gives us a
sufficient level of abstraction for real functional testing.

Please note, that we make no strong assumptions about the existence of
some ZODB working in background or similar. While in fact here a ZODB
is working, the tests do not reflect this. We therefore can deploy non-Zope-specific packages like WebOb_.

One of the main parts of this test module therefore is the funcarg_
function `pytest_funcarg__apps` that sets up a complete WSGI
application and returns it together with a `SampleApp` object stored
somewhere.

To do the complete setup `pytest_funcarg__apps` calls the
`zope.pytest` function :func:`zope.pytest.create_app` with a
`SampleApp` instance to be stored in the
database. :func:`zope.pytest.create_app` stores this instance under
the name ``test`` in the DB root and returns a ready-to-use WSGI
application along with the `SampleApp` instance created.

In the first functional test (`test_browser`) we create and perform an
HTTP request that is sent to the setup WSGI application and check the
output returned by that request. Please note that we use
``http://localhost/test/index.html`` as URL. That's because
:func:`zope.pytest.create_app` stores our application under the name
``test`` in the DB and we registered the view on `SampleApp` objects
under the name ``index.html``.

The second functional test (`test_infrae_browser`) does nearly the
same but this time deploying a faked browser provided by the
:mod:`infrae.testbrowser` package. The latter is well prepared for
simulations of browser sessions, virtual browser clicks, filling out
HTML forms and much more you usually do with a browser. See the
`infrae.testbrowser documentation`_ for details.

Usage of :mod:`infrae.testbrowser`, however, requires Python 2.6 at
least. We therefore expect the respective test to fail if using older
Python versions and mark this condition with a ``@pytest.mark.xfail``
decorator. Another great feature of `py.test` (see `py.test skip and
xfail mechanisms <http://www.pytest.org/skipping.html>`_ for details).

.. doctest::
   :hide:

    >>> mypkg_dir = register_fixture('browser')

Finally, when run, all tests pass:

    >>> import pytest
    >>> pytest.main(mypkg_dir)
    =============...=== test session starts ====...================
    platform ... -- Python 2... -- pytest-...
    collecting ...collected 8 items
    <BLANKLINE>
    .../mypkg3/tests/test_app.py ...
    .../mypkg3/tests/test_browser.py ...
    .../mypkg3/tests/test_foo.py ..
    <BLANKLINE>
    =============...=== ... passed... in ... seconds ===...=============
    0

.. doctest::
   :hide:

    >>> unregister_fixture(mypkg_dir)


.. _ZCML: http://docs.zope.org/zopetoolkit/codingstyle/zcml-style.html
.. _pytest: http://pytest.org/
.. _py.test: http://pytest.org/
.. _funcarg: http://pytest.org/funcargs.html
.. _WebOb: http://pythonpaste.org/webob/
.. _`infrae.testbrowser documentation`: http://infrae.com/download/tools/infrae.testbrowser
