.. _man-functional-testing:

Functional Testing
==================

Introduction
------------

In this chapter, you will learn more about functional testing.  A
doctest based package (``zope.testbrowser``) is used in BlueBream for
functional testing.  Unlike unit tests, functional tests are user
interface (view) oriented.


zope.testbrowser
----------------

The central part of this package is a browser object.  This create this object,
import ``Browser`` class from ``zope.testbrowser.testing``::

  >>> from zope.testbrowser.testing import Browser
  >>> browser = Browser()

To learn the usage of package, first create a simple HTML page with following
content::

  <html>
    <head>
      <title>Test Page</title>
    </head>
    <body>
      <h1>Test Page</h1>
    </body>
  </html>

To open a page::

  >>> browser.open('http://localhost/zopetest/simple.html')
  >>> browser.url
  'http://localhost/zopetest/simple.html'

Test layer
----------

Running tests
-------------

Your test suites can be placed in ``tests.py`` module under each
packages.  By default, in BlueBream there will be a ``tests.py`` with
one test suite created using ``z3c.testsetup``::

  import z3c.testsetup

  test_suite = z3c.testsetup.register_all_tests('tc.main')


The ``z3c.testsetup`` will aut-recover test suites from doctest
files.  You can create your doctest files, similar to example given
in ``README.txt``::

  ticketcollector

  :doctest:
  :functional-zcml-layer: ftesting.zcml

  Open browser and test::

    >>> from zope.testbrowser.testing import Browser
    >>> browser = Browser()
    >>> browser.open('http://localhost/@@index')
    >>> 'Welcome to BlueBream' in browser.contents
    True

The fouth line specifies that a ZCML file named ``ftesting.zcml`` is
required to setup the test layer.

To run the tests::

  $ ./bin/test


.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
