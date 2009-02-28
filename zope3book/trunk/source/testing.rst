Testing
=======


Introduction
------------

Zope 3 gained its incredible stability from testing any code in great
detail.  Zope 3 packages has almost 100% test coverage.  Zope 3
developers write unit tests, and integration tests wherever required.
This chapter introduces unit tests and integration tests and some of
the subtleties.


Unit testing
------------

.. index::
   single: unit testing; testing

You can write unit tests using Python's built-in module called,
`unittest` or other third party modules like `zope.testing`, `nose`
and `py.test`.  There is another approach called, doctest which use
plain text files to write unit tests.  Doctests are the most widely
technique to write unit tests in Zope 3.  During the development and
maintenance of Zope 3 packages, developers use test driven
development (TDD) style process.

To explain the idea of unit testing, consider a use case.  A module
is required with a function which accepts one argument (`name`) and
return: "Good morning, name!".  Before writing the real code, write
the unit test for this.  In fact, you will be writing the real code
and its test cases almost in parallel.  So, create a file named
`example1.py` with the following function definition::

  def goodmorning(name):
      "This returns a good morning message"

Here, you have not yet written the logic.  But this is necessary to
run tests, initially with failures.  Now, create a file named
`example1.txt` with test cases.  You can use reStructuredText
format::

  These are test cases for example1 module.

  First import the module::

    >>> import example1

  Now call the function `goodmorning` without any arguments::

    >>> example1.goodmorning()
    Traceback (most recent call last):
    ...
    TypeError: goodmorning() takes exactly 1 argument (0 given)

  Now call the function goodmorning with one argument::

    >>> example1.goodmorning('Jack')
    'Good morning, Jack!'

Here, the examples are written like executed from prompt.  You can
use your python prompt and copy paste from there.  Finally, create
another file names `test_example1.py` with this content::

  import unittest
  import doctest

  def test_suite():
      return unittest.TestSuite((
          doctest.DocFileSuite('example1.txt'),
          ))

  if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')

This is just a boilerplate code for running the tests.  Now, run the
test using ``python2.5 test_example1.py`` command.  You will get
output with following text::

  File "example1.txt", line 16, in example1.txt
  Failed example:
      example1.goodmorning('Jack')
  Expected:
      'Good morning, Jack!'
  Got nothing

As you can see, one test is failed.  So, implement the function now::

  def goodmorning(name):
      "This returns a good morning message"
      return "Good morning, %s!" % name

Run the test again, it should run without any failures.

Now start thinking about other functionalities required for the
module.  Before start coding, write about it in text file.  Decide
API, write test, write code, then continue this cycle until you
finish your requirements.


Running tests
-------------

.. index::
   single: running tests; testing

In Zope 3, you can use the Buildout recipe named
`zc.recipe.testrunner` for running test cases.  It will create a
script to run the test cases.  For a typical project, you can add
`test` part in configuration like this::

  [buildout]
  parts = test

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector [test]

.. index::
   single: test runner; testing

Here, the package names is assumed as `ticketcollector` (this is the
name you given in `setup.py`).  Also here I assume that there is an
`extras_require` argument for `setup` function in `setup.py`.  The
argument can be given something like this::

  extras_require=dict(test=['zope.app.testing',
                            'zope.testbrowser',
			   ]),

By conventions your test modules are put in `tests` module under each
package.  But the doctest files can be placed in the package itself.
For example if the package is `ticketcollector`, then, the main
doctest file can be placed in `ticketcollector/README.txt`.  And
create a sub-package `ticketcollector.tests`, under this package
create test modules like `test_main.py`, `test_extra.py` etc.  To run
the unit tests, change to instance home::

  $ cd ticketcollector
  $ ./bin/buildout
  $ ./bin/test


Integration testing
-------------------

A doctest based testing module named, ``zope.testbrowser`` is used
for integration/functional testing in Zope 3.  Zope use the term
"functional" more frequently than "integration".  Unlike unit tests,
functional tests are user interface (view) oriented.

The central part of this package is a browser object.  First you have
to create the browser object, to do so, import ``Browser`` class from
``zope.testbrowser.testing``::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()

To open a page::

  >>> browser.open('http://localhost/zopetest/simple.html')
  >>> browser.url
  'http://localhost/zopetest/simple.html'

The ``zope.testbrowser.browser`` module exposes a ``Browser`` class that
simulates a web browser similar to Mozilla Firefox or IE.

    >>> from zope.testbrowser.browser import Browser
    >>> browser = Browser()

This version of the browser object can be used to access any web site just as
you would do using a normal web browser.

There is also a special version of the ``Browser`` class used to do
functional testing of Zope 3 applications, it can be imported from
``zope.testbrowser.testing``:

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()

An initial page to load can be passed to the ``Browser`` constructor:

    >>> browser = Browser('http://localhost/@@/testbrowser/simple.html')
    >>> browser.url
    'http://localhost/@@/testbrowser/simple.html'

The browser can send arbitrary headers; this is helpful for setting the
"Authorization" header or a language value, so that your tests format values
the way you expect in your tests, if you rely on zope.i18n locale-based
formatting or a similar approach.

    >>> browser.addHeader('Authorization', 'Basic mgr:mgrpw')
    >>> browser.addHeader('Accept-Language', 'en-US')

An existing browser instance can also `open` web pages:

    >>> browser.open('http://localhost/@@/testbrowser/simple.html')
    >>> browser.url
    'http://localhost/@@/testbrowser/simple.html'


Summary
-------

This chapter gives a brief hands-on introduction to writing unit
tests.
