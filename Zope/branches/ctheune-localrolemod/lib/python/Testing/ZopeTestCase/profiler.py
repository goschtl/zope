#
# Profiling support for ZTC
#

# $Id: profiler.py,v 1.2 2004/01/12 18:45:42 shh42 Exp $

import os, sys

from profile import Profile
from pstats import Stats

_profile = Profile()
_have_stats = 0

limit = ('.py:', 200)
sort = ('cumulative', 'time', 'pcalls')
strip_dirs = 1


def runcall(*args, **kw):
    global _have_stats
    _have_stats = 1
    return apply(_profile.runcall, args, kw)


def print_stats(limit=limit, sort=sort, strip_dirs=strip_dirs):
    if _have_stats:
        stats = Stats(_profile)
        if strip_dirs:
            stats.strip_dirs()
        apply(stats.sort_stats, sort)
        apply(stats.print_stats, limit)


def dump_stats(filename):
    if _have_stats:
        _profile.dump_stats(filename)
    

class Profiled:
    '''Derive from this class and an xTestCase to get profiling support::

           class MyTest(Profiled, ZopeTestCase):
               ...

       Then run the test module by typing::

           $ python testSomething.py profile

       Profiler statistics will be printed after the test results.
    '''

    def runcall(self, *args, **kw):
        return apply(runcall, args, kw)

    def __call__(self, result=None):
        if result is None: result = self.defaultTestResult()
        result.startTest(self)
        testMethod = getattr(self, self._TestCase__testMethodName)
        try:
            try:
                if int(os.environ.get('PROFILE_SETUP', 0)):
                    self.runcall(self.setUp)
                else:
                    self.setUp()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._TestCase__exc_info())
                return

            ok = 0
            try:
                if int(os.environ.get('PROFILE_TESTS', 0)):
                    self.runcall(testMethod)
                else:
                    testMethod()
                ok = 1
            except self.failureException:
                result.addFailure(self, self._TestCase__exc_info())
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._TestCase__exc_info())

            try:
                if int(os.environ.get('PROFILE_TEARDOWN', 0)):
                    self.runcall(self.tearDown)
                else:
                    self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._TestCase__exc_info())
                ok = 0
            if ok: result.addSuccess(self)
        finally:
            result.stopTest(self)

