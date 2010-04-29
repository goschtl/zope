zope.monkeypatches.doctest
==========================

This product monkeypatches stdlibs doctest to get rid of bugs that 
zope.testing.doctest had fixed. It's useful if you really can't work
around those bugs other ways.

It achieves the bugfixing via monkey-patches, which is horrid, so in general
it's better if you don't use this product.

Bugfix: Unicode output
----------------------

LP #69988 and #144569 both assert that doctests fail when rendering
non-ASCII output with a UnicodeDecodeError.  However, this does not appear
to be so:

  >>> print u'abc'
  abc

  >>> print u'\xe9'.encode('utf-8')
  é

Tests for LP #561568:

  >>> v = u'foo\xe9bar'
  >>> v # doctest: +ELLIPSIS
  u'foo...bar'

  >>> v.encode('utf-8') # doctest: +ELLIPSIS
  'foo...bar'


Bugfix: Inconsistent linefeeds
------------------------------

Due to the way releases are made on different platforms, we sometimes test
files on a *nix system with Windows file endings. Unfortunately, that leaves
some of the test files broken:

  >>> import tempfile
  >>> import os
  >>> fd, fn = tempfile.mkstemp()
  >>> f = os.fdopen(fd, 'wb')
  >>> f.write('Test:\r\n\r\n  >>> x = 1 + 1\r\n\r\nDone.\r\n')
  >>> f.close()

Let's now run it as a doctest:

  >>> import doctest
  >>> failed, run = doctest.testfile(fn, False)
  >>> failed, run
  (0, 1)

It worked. Let's also try the test file suite:

  >>> import unittest
  >>> result = unittest.TestResult()
  >>> doctest.DocFileSuite(fn, module_relative=False).run(result) #doctest: +ELLIPSIS
  <...TestResult run=1 errors=0 failures=0>
  
Remove the temporary test:

  >>> os.remove(fn)


Bugfix: REPORT_ONLY_FIRST_FAILURE and REPORT_xDIFF flags
--------------------------------------------------------

If you tell the testrunner that you want to report only the first failure,
but the test is set up to have a report flag of some sort, like a REPORT_NDIFF,
the REPORT_ONLY_FIRST_FAILURE will be ignored. That's silly, so we patch that.

XXX/TODO: Write tests for it.
