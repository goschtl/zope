======
README
======

This package offers a profiler including a skin. This profiler allows you to 
profile views on a existing Zope3 application.

Let's access the profiler start page:

  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost/++skin++Profiler')

If you access the profiler, you can push the start button:

  >>> print user.contents
