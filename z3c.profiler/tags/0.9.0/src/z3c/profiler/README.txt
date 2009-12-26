==================
Web-based Profiler
==================

This package offers a profiler including a skin. This profiler allows
you to profile views on a existing Zope3 application.

Let's access the profiler start page:

  >>> from z3c.etestbrowser.testing import ExtendedTestBrowser
  >>> user = ExtendedTestBrowser()
  >>> user.addHeader('Accept-Language', 'en')
  >>> user.open('http://localhost/++skin++Profiler')

If you access the profiler, you can push the start button:

  >>> user.getControl('Start').click()
  >>> 'Show Profile' in user.contents
  True

Now we can go to the ``help.html`` page which gets profiled. Let's use
another browser for this.

  >>> newBrowser = ExtendedTestBrowser()
  >>> newBrowser.open('http://localhost/++skin++Profiler/help.html')
  >>> newBrowser.url
  'http://localhost/++skin++Profiler/help.html'

After calling the ``help.html`` page, we can go to the ``doProfile``
page and show the profile by clicking on the ``Show Profile`` button:

  >>> user.getControl('Show Profile').click()

If we whould not call this form within this test, we whould see the
profile data table. But we do not see the profile data table. Probably
the testrunner conflicts with the monkey call.
