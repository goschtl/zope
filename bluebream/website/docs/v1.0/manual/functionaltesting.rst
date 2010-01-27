Functional Testing
==================

Introduction
------------

In this chapter, you will learn more about functional testing.  A doctest based
package (``zope.testbrowser``) is used in Zope 3 for functional testing.
Unlike unit tests, functional tests are user interface (view) oriented.


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


Running tests
-------------

By conventions your functional test modules are put in `ftests` packages under
each main packages.  But the doctest files can be placed in the package itself.
Create a sub-package `zopetic.ftests`, under this package create test modules
like `test_main.py`, `test_extra.py` etc.

To run the functional tests, change to instance home::

  $ cd $HOME/myzope/etc
  $ ../bin/test

Note that, for unit test 'vpu' is used and here it is 'vpf'.

.. raw:: html

  <div id="disqus_thread"></div><script type="text/javascript"
  src="http://disqus.com/forums/bluebream/embed.js"></script><noscript><a
  href="http://disqus.com/forums/bluebream/?url=ref">View the
  discussion thread.</a></noscript><a href="http://disqus.com"
  class="dsq-brlink">blog comments powered by <span
  class="logo-disqus">Disqus</span></a>
