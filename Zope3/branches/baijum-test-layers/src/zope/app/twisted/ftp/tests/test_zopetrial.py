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
"""Contains helper functions and monkey patch to integrate twisted trial
tests with the Zope testrunner.

This code will be unneeded when Twisted 2.3 comes out has it contains
code to integrate itself with any pyunit system. But we it need it now to
integrate the test_zope_ftp tests with the zope.testing test runner.

Michael Kerrin <michael.kerrin@openapp.biz>

$Id$
"""
__docformat__="restructuredtext"

import unittest
from zope.testing import doctest
import sets
import time
import sys
import os
import gc
import re

import twisted.python.failure
import twisted.trial.unittest
import twisted.trial.reporter
import twisted.trial.util
import zope.testing.testrunner

class UnsupportedTrialFeature(Exception):
    """A feature of twisted.trial was used that pyunit cannot support."""


class PyUnitResultAdapter(object):
    def __init__(self, original):
        self.original = original

    def _exc_info(self, err):
        from twisted.trial import reporter
        if isinstance(err, twisted.python.failure.Failure):
            # Unwrap the Failure into a exc_info tuple.
            # XXX: if err.tb is a real traceback and not stringified, we should
            #      use that.
            err = (err.type, err.value, None)
        return err

    def startTest(self, method):
        self.original.startTest(method)

    def stopTest(self, method):
        self.original.stopTest(method)

    def addFailure(self, test, fail):
        if self.original.options.verbose > 2:
            print " (%.3f ms)" % (time.time() - self.original._start_time)

        self.original.failures.append((test, fail.getTraceback()))
        print
        print "Failure in test %s" % test
        print fail.getTraceback()

        if self.original.options.post_mortem:
            zope.testing.testrunner.post_mortem(exc_info)

        self.original.test_width = self.original.last_width = 0

    def addError(self, test, error):
        if self.original.options.verbose > 2:
            print " (%.3f ms)" % (time.time() - self.original._start_time)

        self.original.errors.append((test, error.getTraceback()))
        print
        print "Error in test %s" % test
        print error.getTraceback()

        if self.original.options.post_mortem:
            if self.original.options.resume_layer:
                print
                print '*'*70
                print ("Can't post-mortem debug when running a layer"
                       " as a subprocess!")
                print '*'*70
                print
            else:
                zope.testing.testrunner.post_mortem(exc_info)

        self.original.test_width = self.original.last_width = 0

    def _unsupported(self, test, feature, info):
        self.original.addFailure(
            test, 
            (UnsupportedTrialFeature, 
             UnsupportedTrialFeature(feature, info), 
             None))

    def addSkip(self, test, reason):
        self._unsupported(test, 'skip', reason)

    def addUnexpectedSuccess(self, test, todo):
        self._unsupported(test, 'unexpected success', todo)
        
    def addExpectedFailure(self, test, error):
        self._unsupported(test, 'expected failure', error)

    def addSuccess(self, test):
        self.original.addSuccess(test)

    def upDownError(self, method, warn = True, printStatus = True):
        pass

    def cleanupErrors(self, errs):
        pass
    
    def startSuite(self, name):
        pass


orig_run = twisted.trial.unittest.TestCase.run

def new_run(self, result):
    if not isinstance(result, twisted.trial.reporter.Reporter):
        result = PyUnitResultAdapter(result)
    orig_run(self, result)
    try:
        twisted.trial.util._Janitor().postCaseCleanup()
    except:
        result.cleanupErrors(twisted.python.failure.Failure(sys.exc_info()))

def patchtrial():
    #
    # Patch the twisted.trial.unittest.TestCase class inorder for it to run
    # within the Zope testrunner. Only patch this class if we need to. Newer
    # versions of Twisted don't need to be patched.
    #
    try:
        twisted.trial.unittest.PyUnitResultAdapter
    except AttributeError:
        ## old version of twisted we need to patch twisted.
        twisted.trial.unittest.TestCase.run = new_run

def killthreads():
    """A lot of tests will start threads which the Zope testrunner complains
    about. You can use this method to kill off these threads.
    """
    from twisted.internet import reactor, interfaces
    from twisted.python import threadpool
    if interfaces.IReactorThreads.providedBy(reactor):
        reactor.suggestThreadPoolSize(0)
        if reactor.threadpool:
            reactor.threadpool.stop()
            reactor.threadpool = None
            reactor.threadpool = threadpool.ThreadPool(0, 10)
            reactor.threadpool.start()

orig_configure_logging = zope.testing.testrunner.configure_logging

def setUp(test):
    # This setup is for testing the trial integration. This test indirectly
    # call the zope.testing.testrunner.configure_logging method which tries
    # to reconfigure the logging. This causes problems with some of the other
    # tests. Nullify this method now, this should OK since the logging should
    # all be set up at this stage.
    zope.testing.testrunner.configure_logging = lambda : None

    test.globs['this_directory'] = os.path.split(__file__)[0]
    test.globs['saved-sys-info'] = (
        sys.path[:],
        sys.argv[:],
        sys.modules.copy(),
        gc.get_threshold(),
        )
    test.globs['testrunner_script'] = __file__


def tearDown(test):
    # redefine the configure_logging method that we nullified in the setUp
    # for these tests.
    zope.testing.testrunner.configure_logging = orig_configure_logging

    sys.path[:], sys.argv[:] = test.globs['saved-sys-info'][:2]
    gc.set_threshold(*test.globs['saved-sys-info'][3])
    sys.modules.clear()
    sys.modules.update(test.globs['saved-sys-info'][2])

def test_suite():
    # patch trial before starting so that our test fail when they should.
    patchtrial()

    # copied from zope.testing.testrunner
    import zope.testing.renormalizing
    checker = zope.testing.renormalizing.RENormalizing([
        (re.compile('^> [^\n]+->None$', re.M), '> ...->None'),
        (re.compile('\\\\'), '/'),   # hopefully, we'll make windows happy
        (re.compile('/r'), '\\\\r'), # undo damage from previous
        (re.compile(r'\r'), '\\\\r\n'),
        (re.compile(r'\d+[.]\d\d\d seconds'), 'N.NNN seconds'),
        (re.compile(r'\d+[.]\d\d\d ms'), 'N.NNN ms'),
        (re.compile('( |")[^\n]+testrunner-ex'), r'\1testrunner-ex'),
        (re.compile('( |")[^\n]+testrunner.py'), r'\1testrunner.py'),
        (re.compile(r'> [^\n]*(doc|unit)test[.]py\(\d+\)'),
         r'\1doctest.py(NNN)'),
        (re.compile(r'[.]py\(\d+\)'), r'.py(NNN)'),
        (re.compile(r'[.]py:\d+'), r'.py:NNN'),
        (re.compile(r' line \d+,', re.IGNORECASE), r' Line NNN,'),

        # omit traceback entries for unittest.py or doctest.py from
        # output:
        (re.compile(r'^ +File "[^\n]+(doc|unit)test.py", [^\n]+\n[^\n]+\n',
                    re.MULTILINE),
         r''),
        (re.compile('^> [^\n]+->None$', re.M), '> ...->None'),
        (re.compile('import pdb; pdb'), 'Pdb()'), # Py 2.3
        ])
    
    suites = [
        doctest.DocFileSuite('trial.txt',
                             setUp = setUp, tearDown = tearDown,
                             optionflags = doctest.ELLIPSIS,
                             checker = checker),
        ]

    return unittest.TestSuite(suites)
