=============
Test Recorder
=============

The testrecorder is a browser-based tool to support the rapid
development of functional tests for Web-based systems and
applications.  The idea is to "record" tests by exercising whatever is
to be tested within the browser.  The test recorder will turn a
recorded session into a functional test.


Output
------

Test recorder supports two output modes:

Selenium
  In this mode, the testrecorder spits out HTML markup that lets you
  recreate the browser test using the Selenium_ functional testing
  framework.

Test browser
  In this mode, the testrecorder spits out a Python doctest_ that
  exercises a functional test using the Zope testbrowser_.  The Zope
  testbrowser allows you to programmatically simulate a browser from
  Python code.  Its main use is to make functional tests easy and
  runnable without a browser at hand.  It is used in Zope, but is not
  tied to Zope at all.

.. _Selenium: http://www.openqa.org/selenium/
.. _doctest: http://docs.python.org/lib/module-doctest.html
.. _testbrowser: http://cheeseshop.python.org/pypi/ZopeTestbrowser


Usage
-----

Like Selenium and the Zope test browser, the test recorder can very
well be used to test any web application, be it Zope-based or not.  Of
course, it was developed by folks from the Zope community for use with
Zope.
