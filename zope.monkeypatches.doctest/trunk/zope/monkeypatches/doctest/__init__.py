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
    return open(filename, 'rU').read(), filename

doctest._load_testfile = _patched_load_testfile


# Patch so you can set REPORT_ONLY_FIRST_FAILURE even if you have a DIFF flag
# on the test.
import sys
from StringIO import StringIO

def _patched_runTest(self):
    test = self._dt_test
    old = sys.stdout
    new = StringIO()
    optionflags = self._dt_optionflags

    if not (optionflags & doctest.REPORTING_FLAGS):
        # The option flags don't include any reporting flags,
        # so add the default reporting flags
        optionflags |= doctest._unittest_reportflags
        
    # This should work even if you have a diff flag:
    if doctest._unittest_reportflags & doctest.REPORT_ONLY_FIRST_FAILURE:
        optionflags |= doctest.REPORT_ONLY_FIRST_FAILURE

    runner = doctest.DocTestRunner(optionflags=optionflags,
                           checker=self._dt_checker, verbose=False)

    try:
        runner.DIVIDER = "-"*70
        failures, tries = runner.run(
            test, out=new.write, clear_globs=False)
    finally:
        sys.stdout = old

    if failures:
        raise self.failureException(self.format_failure(new.getvalue()))
    
doctest.DocTestCase.runTest = _patched_runTest
    

def test_suite():
    return doctest.DocFileSuite('README.txt')