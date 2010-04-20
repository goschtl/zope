__all__ = [
    # 0, Option Flags
    'register_optionflag',
    'DONT_ACCEPT_TRUE_FOR_1',
    'DONT_ACCEPT_BLANKLINE',
    'NORMALIZE_WHITESPACE',
    'ELLIPSIS',
    'SKIP',
    'IGNORE_EXCEPTION_DETAIL',
    'COMPARISON_FLAGS',
    'REPORT_UDIFF',
    'REPORT_CDIFF',
    'REPORT_NDIFF',
    'REPORT_ONLY_FIRST_FAILURE',
    'REPORTING_FLAGS',
    # 1. Utility Functions
    # 2. Example & DocTest
    'Example',
    'DocTest',
    # 3. Doctest Parser
    'DocTestParser',
    # 4. Doctest Finder
    'DocTestFinder',
    # 5. Doctest Runner
    'DocTestRunner',
    'OutputChecker',
    'DocTestFailure',
    'UnexpectedException',
    'DebugRunner',
    # 6. Test Functions
    'testmod',
    'testfile',
    'run_docstring_examples',
    # 7. Tester
    'Tester',
    # 8. Unittest Support
    'DocTestSuite',
    'DocFileSuite',
    'set_unittest_reportflags',
    # 9. Debugging Support
    'script_from_examples',
    'testsource',
    'debug_src',
    'debug',
]

# Tell people to use the builtin module instead.
import warnings
warnings.warn('zope.testing.doctest is deprecated in favour of '
              'the Python standard library doctest module', DeprecationWarning,
               stacklevel=2)


# Patch to fix an error that makes subsequent tests fail after you have
# returned unicode in a test.
import doctest

_org_SpoofOut = doctest._SpoofOut
class _patched_SpoofOut(_org_SpoofOut):
    def truncate(self,   size=None):
        _org_SpoofOut.truncate(self, size)
        if not self.buf:
            self.buf = ''

doctest._SpoofOut = _patched_SpoofOut


# Patch to fix tests that has mixed line endings:
import os

def _patched_load_testfile(filename, package, module_relative):
    if module_relative:
        package = doctest._normalize_module(package, 3)
        filename = doctest._module_relative_path(package, filename)
        if hasattr(package, '__loader__'):
            if hasattr(package.__loader__, 'get_data'):
                file_contents = package.__loader__.get_data(filename)
                # get_data() opens files as 'rb', so one must do the equivalent
                # conversion as universal newlines would do.
                return file_contents.replace(os.linesep, '\n'), filename
    return open(filename, 'U').read(), filename

doctest._load_testfile = _patched_load_testfile


# Use a special exception for the test runner:
from zope.testing.exceptions import DocTestFailureException
doctest.DocTestCase.failureException = DocTestFailureException


# Patch to let the doctest have the globals of the testcase
import unittest

def _patched_init(self, test, optionflags=0, setUp=None, tearDown=None,
             checker=None):
    unittest.TestCase.__init__(self)
    self._dt_optionflags = optionflags
    self._dt_checker = checker
    self._dt_test = test
    self._dt_setUp = setUp
    self._dt_tearDown = tearDown
    self._dt_globs = test.globs.copy()

def _patched_tearDown(self):
    test = self._dt_test

    if self._dt_tearDown is not None:
        self._dt_tearDown(test)

    test.globs.clear()
    test.globs.update(self._dt_globs)

doctest.DocTestCase.__init__ = _patched_init
doctest.DocTestCase.tearDown = _patched_tearDown

    
from doctest import *
