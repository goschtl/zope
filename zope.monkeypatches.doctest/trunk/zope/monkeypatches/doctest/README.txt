zope.monkeypatches.doctest
==========================

This product monkeypatches stdlibs doctest to get rid of bugs that 
zope.testing.doctest had fixed. It's useful if you really can't work
around those bugs other ways.

It achieves the bugfixing via monkey-patches, which is horrid, so in general
it's better if you don't use this product. Of these bugs, the unicode bug
is not relevant and the Windows lineending bug seems to be fixed. The 
report flag issue is an issue in Python 3, and this module will run under
Python 3.1 and fix that issue. However, the tests will fail. This may or
may not change in the future. :)

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
files on a Unix system with Windows file endings. Unfortunately, that leaves
some of the test files broken:

  >>> import tempfile
  >>> import os
  >>> fd, fn = tempfile.mkstemp()
  >>> f = os.fdopen(fd, 'w')
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

  >>> code = '''def fn():
  ...     """This should fail:
  ...     >>> assert 1 == 2
  ...     True
  ...
  ...     >>> assert 2 == 1
  ...     True
  ...     """
  ...     return None'''
  >>> import imp
  >>> newmodule = imp.new_module('newmodule')
  >>> exec(code, newmodule.__dict__)
  >>> suite = doctest.DocTestSuite(newmodule, optionflags=doctest.REPORT_NDIFF)
  >>> doctest.set_unittest_reportflags(doctest.REPORT_ONLY_FIRST_FAILURE)
  0
  >>> runner = doctest.DocTestRunner()
  >>> for case in suite: #doctest: +ELLIPSIS
  ...   case.runTest()
  Traceback (most recent call last):
  ...
      compileflags, 1) in test.globs
    File "<doctest README.txt[25]>", line 2, in ...
      case.runTest()
  ...
      raise self.failureException(self.format_failure(new.getvalue()))
  AssertionError: Failed doctest test for newmodule.fn
    File "newmodule", line 1, in fn
  <BLANKLINE>
  ----------------------------------------------------------------------
  File "newmodule", line 3, in newmodule.fn
  Failed example:
      assert 1 == 2
  Exception raised:
      Traceback (most recent call last):
  ...
          compileflags, 1) in test.globs
        File "<doctest newmodule.fn[0]>", line 1, in ...
          assert 1 == 2
      AssertionError
  <BLANKLINE>
  