##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Contains helper functions and monkey patches to integrate twisted trial
tests with the zope testrunner.

WARNING - use with care - actaully just DO NOT USE THIS CODE. I only wrote
his to test the ftp server and the only the ftp server. It should NOT be used
for anything else. If we need to integrate the twisted trial framework and the
zope.testing testrunner for anything else we need to think about this and come
up with something better. Seriously.

Twisted wraps all failures inside twisted.python.failure.Failure objects, and
it also catches every exception thrown so I need this code to make my tests
fail when they are broken. Otherwise they will always pass with the exception
of syntax errors.

Michael Kerrin <michael.kerrin@openapp.biz>

$Id$
"""
__docformat__="restructuredtext"

import unittest

import twisted.trial.unittest
from twisted.python.failure import Failure

import zope.testing.testrunner
from zope.testing.testrunner import TestResult

from twisted.trial import util

old_addError = zope.testing.testrunner.TestResult.addError
old_addFailure = zope.testing.testrunner.TestResult.addFailure

RUNNING_TESTS = False

def print_traceback(msg, exc_info):
    print
    print msg

    tb = "".join(exc_info.getTraceback())

    print tb


def new_addError(self, test, exc_info):
    if isinstance(exc_info, Failure):
        if self.options.verbose > 2:
            print " (%.3f ms)" % (time.time() - self._start_time)
        self.errors.append((test, exc_info.getTraceback()))

        if not RUNNING_TESTS:
            print
            print_traceback("Error in test %s" % test, exc_info)

        if self.options.post_mortem:
            if self.options.resume_layer:
                print
                print '*'*70
                print ("Can't post-mortem debug when running a layer"
                       " as a subprocess!")
                print '*'*70
                print
            else:
                zope.testing.testrunner.post_mortem(exc_info)

        self.test_width = self.last_width = 0
    else:
        old_addError(self, test, exc_info)


def new_addFailure(self, test, exc_info):
    if isinstance(exc_info, Failure):
        if self.options.verbose > 2:
            print " (%.3f ms)" % (time.time() - self._start_time)

        self.failures.append((test, exc_info.getTraceback()))

        if not RUNNING_TESTS:
            print
            print_traceback("Failure in test %s" % test, exc_info)

        if self.options.post_mortem:
            zope.testing.testrunner.post_mortem(exc_info)

        self.test_width = self.last_width = 0
    else:
        old_addFailure(self, test, exc_info)


def setUp():
    # IMPORTANT - call the tearDown method below if you use this method!!!
    #

    # Monkey-patch the twisted.trial so has to catch and handle
    # twisted.python.failure.Failure object correctly.
    zope.testing.testrunner.TestResult.addError = new_addError
    zope.testing.testrunner.TestResult.addFailure = new_addFailure

def tearDown():
    # IMPORTANT - call this method!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #

    # Un-Monkey-patch the twisted.trial so has to catch and handle
    # twisted.python.failure.Failure object correctly.
    zope.testing.testrunner.TestResult.addError = new_addError
    zope.testing.testrunner.TestResult.addFailure = new_addFailure

    # Something funny happens with threads, the twisted reactor and zope.
    # This fixes it.
    util._Janitor.do_cleanThreads()

#
# Now just make sure that all this does what it says.
#

class TestZopeTests(unittest.TestCase):

    def setUp(self):
        setUp()

    def tearDown(self):
        tearDown()

    def test_error(self):
        raise Exception, "this test is a broken zope test :-)"

    def test_failure(self):
        self.assert_(False, "I am a failed zope test")

    def test_assert_ok(self):
        self.assert_(True, "I am a good test")


class TestTrialTests(twisted.trial.unittest.TestCase):

    def setUp(self):
        setUp()

    def tearDown(self):
        tearDown()

    def test_error(self):
        raise Exception, "this test is a broken trial test :-)"

    def test_failure(self):
        self.assert_(False, "I am a failed trial test")

    def test_assert_ok(self):
        self.assert_(True, "I am a good test")


class Options(object):
    # simple object to simpilutate the minium zope.testing options.
    progress = False
    verbose  = 0
    post_mortem = None


old_print_traceback = zope.testing.testrunner.print_traceback
def new_print_traceback(msg, exc_info):
    # don't print out anything when running the test tests.
    pass


class TestTrialIntegration(unittest.TestCase):

    def run_test(self, name, tests):
        global RUNNING_TESTS

        RUNNING_TESTS = True
        zope.testing.testrunner.print_traceback = new_print_traceback

        result = zope.testing.testrunner.TestResult(Options(), tests)
        for test in tests:
            test(result)

        RUNNING_TESTS = False
        zope.testing.testrunner.print_traceback = old_print_traceback

        return result

    def test_trial_tests(self):
        suite = unittest.makeSuite(TestTrialTests)
        result = self.run_test('', suite)
        self._assertResults(
            'zope.app.twisted.ftp.tests.test_zopetrial.TestTrialTests', result)

    def test_zope_tests(self):
        suite = unittest.makeSuite(TestZopeTests)
        result = self.run_test('', suite)
        self._assertResults(
            'zope.app.twisted.ftp.tests.test_zopetrial.TestZopeTests', result)

    def _assertResults(self, basetest, result):
        # errors
        self.assertEqual(len(result.failures), 1)
        self.assertEqual(result.failures[0][0].id(),
                         '%s.test_failure' % basetest)

        # failures
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0][0].id(), '%s.test_error' % basetest)

        # ok
        self.assertEqual(result.testsRun, 3) # ok, error, failure


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestTrialIntegration))

    return suite

if __name__ == '__main__':
    test_suite()
