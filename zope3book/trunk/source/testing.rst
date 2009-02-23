Testing
=======


Introduction
------------

As you know by now, Zope 3 gains its incredible stability from
testing any code in great detail.  The currently most common method
is to write unit tests. This chapter introduces unit tests - which
are Zope 3 independent - and introduces some of the subtleties.


Unit testing
------------

.. index::
   single: unit testing; testing

Unit test can be written using `unittest`, `zope.unittest`, `nose`,
`py.test` etc.  Another approach to write unit test is using doctest.
Doctest-based unit tests are the most used way to write unit tests in
Zope 3.  During the development and maintenance of Zope 3 packages
developers use test driven development (TDD) style process.

To explain the idea of unit testing, consider a use case.  A module
is required with a function which returns "Good morning, name!".  The
name will be given as an argument.  Before writing the real code
write the unit test for this.  In fact, you will be writing the real
code and it's test cases almost in parallel.  So, create a file named
`example1.py` with the following function definition::

  def goodmorning(name):
      "This returns a good morning message"

See, you have not yet written the logic.  But this is necessary to
run tests successfully with failures!.  Ok, now create a file named
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

See, the examples are written like executed from prompt.  You can use
your python prompt and copy paste from there.  Now create another
file names `test_example1.py` with this content::

  import unittest
  import doctest

  def test_suite():
      return unittest.TestSuite((
          doctest.DocFileSuite('example1.txt'),
          ))

  if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')

This is just boilerplate code for running the test.  Now run the test
using python2.4 test_example1.py command.  You will get output with
following text::

  File "example1.txt", line 16, in example1.txt
  Failed example:
      example1.goodmorning('Jack')
  Expected:
      'Good morning, Jack!'
  Got nothing

Now, one test failed, so, implement the function now::

  def goodmorning(name):
      "This returns a good morning message"
      return "Good morning, %s!" % name

Run the test again, it should run without failures.

Now start thinking about other functionalities required for the
module.  Before start coding write about it in text file.  Decide
API, write test, write code, than continue this cycle until you
finish your requirements.


Running tests
-------------

.. index::
   single: running tests; testing

The Buildout recipe named `zc.recipe.testrunner` would be convenient
for running test cases.  It will create a script to run the test
cases.  For a typical project you can add `test` part in
configuration like this::

  [buildout]
  parts = test

  [test]
  recipe = zc.recipe.testrunner
  eggs = ticketcollector [test]

.. index::
   single: test runner; testing

Here the package names is assumed as `ticketcollector` (this is the
name you given in `setup.py`).  Also here I assume that there is an
`extras_require` argument for `setup` function in `setup.py`.
The argument can be given something like this::

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
  $ ./bin/test


Summary
-------

This chapter gives a brief hands-on introduction to writing unit
tests.
