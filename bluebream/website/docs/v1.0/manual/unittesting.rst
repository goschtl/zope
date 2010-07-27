Unit Testing
============

Introduction
------------

This chapter will discuss about unit testing and integration
testing. Doctest-based testing is heavily used in Zope 3. And test
driven development (TDD) is prefered in Zope 3.  To explain the idea,
consider a use case. A module is required with a function which
returns "Good morning, name!". The name will be given as an
argument. Before writing the real code write the unit test for
this. In fact you will be writing the real code and it's test cases
almost in parallel. So create a file named example1.py with the
function definition::

  def goodmorning(name):
      "This returns a good morning message"

See, you have not yet written the logic. But this is necessary to run
tests successfully with failures!. Ok, now create a file named
example1.txt with test cases, use reStructuredText format::

  These are tests for example1 module.

  First import the module:

    >>> import example1

Now call the function goodmorning without any arguments::

  >>> example1.goodmorning()
  Traceback (most recent call last):
  ...
  TypeError: goodmorning() takes exactly 1 argument (0 given)

Now call the function goodmorning with one argument::

  >>> example1.goodmorning('Jack')
  'Good morning, Jack!'

See the examples are written like executed from prompt. You can use
your python prompt and copy paste from there. Now create another file
test_example1.py with this content::

  import unittest
  import doctest

  def test_suite():
      return unittest.TestSuite((
          doctest.DocFileSuite('example1.txt'),
          ))

  if __name__ == '__main__':
      unittest.main(defaultTest='test_suite')

This is just boilerplate code for running the test. Now run the test
using python2.4 test_example1.py command. You will get output with
following text::

  File "example1.txt", line 16, in example1.txt
  Failed example:
      example1.goodmorning('Jack')
  Expected:
      'Good morning, Jack!'
  Got nothing


Now one test failed, so implement the function now::

  def goodmorning(name):
      "This returns a good morning message"
      return "Good morning, %s!" % name

Now run the test again, it will run without failures.

Now start thinking about other functionalities required for the
module. Before start coding write about it in text file. Decide API,
write test, write code, than continue this cycle until you finish
your requirements.


Running tests
-------------

By conventions your test modules are put in ``tests`` module under
each package.  But the doctest files can be placed in the package
itself.  For example if the package is ticketcollector. Then the main
doctest file can be placed in ticketcollector/README.txt.  And create
a sub-package zopetic.tests, under this package create test modules
like test_main.py, test_extra.py etc.  To run the unit tests, change
to instance home::

  $ cd ticketcollector
  $ ./bin/test

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
