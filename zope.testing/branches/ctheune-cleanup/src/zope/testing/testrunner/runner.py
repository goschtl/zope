##############################################################################
#
# Copyright (c) 2004-2008 Zope Corporation and Contributors.
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
"""Test execution

$Id: __init__.py 86232 2008-05-03 15:09:33Z ctheune $
"""

import re
import cStringIO
import gc
import glob
import os
import pdb
import sys
import tempfile
import threading
import time
import traceback
import unittest

from zope.testing import doctest
from zope.testing.testrunner.find import find_tests, test_dirs
from zope.testing.testrunner.find import StartUpFailure, import_name
from zope.testing.testrunner.find import name_from_layer, _layer_name_cache
from zope.testing.testrunner.refcount import TrackRefs
from zope.testing.testrunner.options import get_options
import zope.testing.testrunner.coverage
import zope.testing.testrunner.doctest
import zope.testing.testrunner.logsupport
import zope.testing.testrunner.selftest
import zope.testing.testrunner.profiling
import zope.testing.testrunner.timing
import zope.testing.testrunner.garbagecollection


PYREFCOUNT_PATTERN = re.compile('\[[0-9]+ refs\]')


class SubprocessError(Exception):
    """An error occurred when running a subprocess
    """

    def __init__(self, reason, stderr):
        self.reason = reason
        self.stderr = stderr

    def __str__(self):
        return '%s: %s' % (self.reason, self.stderr)


class CanNotTearDown(Exception):
    "Couldn't tear down a test"


class EndRun(Exception):
    """Indicate that the existing run call should stop

    Used to prevent additional test output after post-mortem debugging.

    """


class Runner(object):
    """The test runner.

    It is the central point of this package and responsible for finding and
    executing tests as well as configuring itself from the (command-line)
    options passed into it.

    """

    def __init__(self, defaults=None, args=None, found_suites=None,
                 options=None):
        self.defaults = defaults
        self.args = args
        self.found_suites = found_suites
        self.options = options
        self.failed = True

        self.ran = 0
        self.failures = []
        self.errors = []
        self.nlayers = 0

        self.show_report = True

        self.features = []

    def run(self):
        self.configure()
        if self.options.fail:
            return True

        # Global setup
        for feature in self.features:
            feature.global_setup()

        self.find_tests()

        # Late setup
        #
        # Some system tools like profilers are really bad with stack frames.
        # E.g. hotshot doesn't like it when we leave the stack frame that we
        # called start() from.
        for feature in self.features:
            feature.late_setup()

        try:
            self.run_tests()
        finally:
            # Early teardown
            for feature in reversed(self.features):
                feature.early_teardown()
            # Global teardown
            for feature in reversed(self.features):
                feature.global_teardown()

        if self.show_report:
            self.report()
            for feature in self.features:
                feature.report()

    def configure(self):
        if self.args is None:
            self.args = sys.argv[:]

        # Check to see if we are being run as a subprocess. If we are,
        # then use the resume-layer and defaults passed in.
        if len(self.args) > 1 and self.args[1] == '--resume-layer':
            self.args.pop(1)
            resume_layer = self.args.pop(1)
            resume_number = int(self.args.pop(1))
            self.defaults = []
            while len(self.args) > 1 and self.args[1] == '--default':
                self.args.pop(1)
                self.defaults.append(self.args.pop(1))

            sys.stdin = FakeInputContinueGenerator()
        else:
            resume_layer = resume_number = None

        options = get_options(self.args, self.defaults)

        options.testrunner_defaults = self.defaults
        options.resume_layer = resume_layer
        options.resume_number = resume_number

        self.options = options

        # XXX I moved this here mechanically.
        self.test_directories = test_dirs(self.options, {})

        self.features.append(zope.testing.testrunner.selftest.SelfTest(self))
        self.features.append(zope.testing.testrunner.logsupport.Logging(self))
        self.features.append(zope.testing.testrunner.coverage.Coverage(self))
        self.features.append(zope.testing.testrunner.doctest.DocTest(self))
        self.features.append(zope.testing.testrunner.profiling.Profiling(self))
        self.features.append(zope.testing.testrunner.timing.Timing(self))
        self.features.append(zope.testing.testrunner.garbagecollection.Threshold(self))
        self.features.append(zope.testing.testrunner.garbagecollection.Debug(self))

        # Remove all features that aren't activated
        self.features = [f for f in self.features if f.active]

    def find_tests(self):
        global _layer_name_cache
        _layer_name_cache.clear() # Reset to enforce test isolation

        output = self.options.output

        if self.options.resume_layer:
            self.original_stderr = sys.stderr
            sys.stderr = sys.stdout
        elif self.options.verbose:
            if self.options.all:
                msg = "Running tests at all levels"
            else:
                msg = "Running tests at level %d" % self.options.at_level
            output.info(msg)

        # Add directories to the path
        for path in self.options.path:
            if path not in sys.path:
                sys.path.append(path)

        self.tests_by_layer_name = find_tests(self.options, self.found_suites)
        self.import_errors = self.tests_by_layer_name.pop(None, None)
        # XXX move to reporting
        output.import_errors(self.import_errors)

    def run_tests(self):
        """Find and run tests

        Passing a list of suites using the found_suites parameter will cause
        that list of suites to be used instead of attempting to load them from
        the filesystem. This is useful for unit testing the test runner.

        Returns True if there where failures or False if all tests passed.

        """
        if 'unit' in self.tests_by_layer_name:
            tests = self.tests_by_layer_name.pop('unit')
            if (not self.options.non_unit) and not self.options.resume_layer:
                if self.options.layer:
                    should_run = False
                    for pat in self.options.layer:
                        if pat('unit'):
                            should_run = True
                            break
                else:
                    should_run = True

                if should_run:
                    if self.options.list_tests:
                        self.options.output.list_of_tests(tests, 'unit')
                    else:
                        self.options.output.info("Running unit tests:")
                        self.nlayers += 1
                        try:
                            self.ran += run_tests(self.options, tests, 'unit',
                                                  self.failures, self.errors)
                        except EndRun:
                            self.failed = True
                            return

        setup_layers = {}

        layers_to_run = list(ordered_layers(self.tests_by_layer_name))
        if self.options.resume_layer is not None:
            layers_to_run = [
                (layer_name, layer, tests)
                for (layer_name, layer, tests) in layers_to_run
                if layer_name == self.options.resume_layer
            ]
        elif self.options.layer:
            layers_to_run = [
                (layer_name, layer, tests)
                for (layer_name, layer, tests) in layers_to_run
                if filter(None, [pat(layer_name) for pat in self.options.layer])
            ]

        if self.options.list_tests:
            for layer_name, layer, tests in layers_to_run:
                self.options.output.list_of_tests(tests, layer_name)
            self.failed = False
            self.show_report = False
            return

        for layer_name, layer, tests in layers_to_run:
            self.nlayers += 1
            try:
                self.ran += run_layer(self.options, layer_name, layer, tests,
                                      setup_layers, self.failures, self.errors)
            except EndRun:
                self.failed = True
                return
            except CanNotTearDown:
                setup_layers = None
                if not self.options.resume_layer:
                    self.ran += resume_tests(self.options, layer_name, layers_to_run,
                                             self.failures, self.errors)
                    break

        if setup_layers:
            if self.options.resume_layer == None:
                self.options.output.info("Tearing down left over layers:")
            tear_down_unneeded(self.options, (), setup_layers, True)

        self.failed = bool(self.import_errors or self.failures or self.errors)

    def report(self):
        if self.options.resume_layer:
            sys.stdout.close()
            # Communicate with the parent.  The protocol is obvious:
            print >> self.original_stderr, self.ran, len(self.failures), len(self.errors)
            for test, exc_info in self.failures:
                print >> self.original_stderr, ' '.join(str(test).strip().split('\n'))
            for test, exc_info in self.errors:
                print >> self.original_stderr, ' '.join(str(test).strip().split('\n'))

        else:
            if self.options.verbose:
                self.options.output.tests_with_errors(self.errors)
                self.options.output.tests_with_failures(self.failures)

            if self.nlayers != 1:
                self.options.output.totals(self.ran, len(self.failures),
                                           len(self.errors), self.total_time)

            self.options.output.modules_with_import_problems(
                self.import_errors)


def run_tests(options, tests, name, failures, errors):
    repeat = options.repeat or 1
    repeat_range = iter(range(repeat))
    ran = 0

    output = options.output

    gc.collect()
    lgarbage = len(gc.garbage)

    sumrc = 0
    if options.report_refcounts:
        if options.verbose:
            # XXX This code path is untested
            track = TrackRefs()
        rc = sys.gettotalrefcount()

    for iteration in repeat_range:
        if repeat > 1:
            output.info("Iteration %d" % (iteration + 1))

        if options.verbose > 0 or options.progress:
            output.info('  Running:')
        result = TestResult(options, tests, layer_name=name)

        t = time.time()

        if options.post_mortem:
            # post-mortem debugging
            for test in tests:
                if result.shouldStop:
                    break
                result.startTest(test)
                state = test.__dict__.copy()
                try:
                    try:
                        test.debug()
                    except KeyboardInterrupt:
                        raise
                    except:
                        result.addError(
                            test,
                            sys.exc_info()[:2] + (sys.exc_info()[2].tb_next, ),
                            )
                    else:
                        result.addSuccess(test)
                finally:
                    result.stopTest(test)
                test.__dict__.clear()
                test.__dict__.update(state)

        else:
            # normal
            for test in tests:
                if result.shouldStop:
                    break
                state = test.__dict__.copy()
                test(result)
                test.__dict__.clear()
                test.__dict__.update(state)

        t = time.time() - t
        output.stop_tests()
        failures.extend(result.failures)
        errors.extend(result.errors)
        output.summary(result.testsRun, len(result.failures), len(result.errors), t)
        ran = result.testsRun

        gc.collect()
        if len(gc.garbage) > lgarbage:
            output.garbage(gc.garbage[lgarbage:])
            lgarbage = len(gc.garbage)

        if options.report_refcounts:

            # If we are being tested, we don't want stdout itself to
            # foul up the numbers. :)
            try:
                sys.stdout.getvalue()
            except AttributeError:
                pass

            prev = rc
            rc = sys.gettotalrefcount()
            if options.verbose:
                track.update()
                if iteration > 0:
                    output.detailed_refcounts(track, rc, prev)
                else:
                    track.delta = None
            elif iteration > 0:
                output.refcounts(rc, prev)

    return ran


def run_layer(options, layer_name, layer, tests, setup_layers,
              failures, errors):

    output = options.output
    gathered = []
    gather_layers(layer, gathered)
    needed = dict([(l, 1) for l in gathered])
    if options.resume_number != 0:
        output.info("Running %s tests:" % layer_name)
    tear_down_unneeded(options, needed, setup_layers)

    if options.resume_layer != None:
        output.info_suboptimal( "  Running in a subprocess.")

    try:
        setup_layer(options, layer, setup_layers)
    except EndRun:
        raise
    except Exception:
        f = cStringIO.StringIO()
        traceback.print_exc(file=f)
        output.error(f.getvalue())
        errors.append((SetUpLayerFailure(), sys.exc_info()))
        return 0
    else:
        return run_tests(options, tests, layer_name, failures, errors)

class SetUpLayerFailure(unittest.TestCase):

    def runTest(self):
        "Layer set up failure."

def resume_tests(options, layer_name, layers, failures, errors):
    output = options.output
    layers = [l for (l, _, _) in layers]
    layers = layers[layers.index(layer_name):]
    rantotal = 0
    resume_number = 0
    for layer_name in layers:
        args = [sys.executable,
                sys.argv[0],
                '--resume-layer', layer_name, str(resume_number),
                ]
        resume_number += 1
        for d in options.testrunner_defaults:
            args.extend(['--default', d])

        args.extend(options.original_testrunner_args[1:])

        # this is because of a bug in Python (http://www.python.org/sf/900092)
        if (options.profile == 'hotshot'
            and sys.version_info[:3] <= (2,4,1)):
            args.insert(1, '-O')

        if sys.platform.startswith('win'):
            args = args[0] + ' ' + ' '.join([
                ('"' + a.replace('\\', '\\\\').replace('"', '\\"') + '"')
                for a in args[1:]
                ])

        subin, subout, suberr = os.popen3(args)
        while True:
            try:
                for l in subout:
                    sys.stdout.write(l)
            except IOError, e:
                if e.errno == errno.EINTR:
                    # If the subprocess dies before we finish reading its
                    # output, a SIGCHLD signal can interrupt the reading.
                    # The correct thing to to in that case is to retry.
                    continue
                output.error("Error reading subprocess output for %s" % layer_name)
                output.info(str(e))
            else:
                break

        line = suberr.readline()
        try:
            ran, nfail, nerr = map(int, line.strip().split())
        except KeyboardInterrupt:
            raise
        except:
            raise SubprocessError(
                'No subprocess summary found', line+suberr.read())

        while nfail > 0:
            nfail -= 1
            failures.append((suberr.readline().strip(), None))
        while nerr > 0:
            nerr -= 1
            errors.append((suberr.readline().strip(), None))

        rantotal += ran

    return rantotal



def tear_down_unneeded(options, needed, setup_layers, optional=False):
    # Tear down any layers not needed for these tests. The unneeded
    # layers might interfere.
    unneeded = [l for l in setup_layers if l not in needed]
    unneeded = order_by_bases(unneeded)
    unneeded.reverse()
    output = options.output
    for l in unneeded:
        output.start_tear_down(name_from_layer(l))
        t = time.time()
        try:
            if hasattr(l, 'tearDown'):
                l.tearDown()
        except NotImplementedError:
            output.tear_down_not_supported()
            if not optional:
                raise CanNotTearDown(l)
        else:
            output.stop_tear_down(time.time() - t)
        del setup_layers[l]


cant_pm_in_subprocess_message = """
Can't post-mortem debug when running a layer as a subprocess!
Try running layer %r by itself.
"""

def setup_layer(options, layer, setup_layers):
    assert layer is not object
    output = options.output
    if layer not in setup_layers:
        for base in layer.__bases__:
            if base is not object:
                setup_layer(options, base, setup_layers)
        output.start_set_up(name_from_layer(layer))
        t = time.time()
        if hasattr(layer, 'setUp'):
            try:
                layer.setUp()
            except Exception:
                if options.post_mortem:
                    if options.resume_layer:
                        options.output.error_with_banner(
                            cant_pm_in_subprocess_message
                            % options.resume_layer)
                        raise
                    else:
                        post_mortem(sys.exc_info())
                else:
                    raise

        output.stop_set_up(time.time() - t)
        setup_layers[layer] = 1


class TestResult(unittest.TestResult):

    def __init__(self, options, tests, layer_name=None):
        unittest.TestResult.__init__(self)
        self.options = options
        # Calculate our list of relevant layers we need to call testSetUp
        # and testTearDown on.
        if layer_name != 'unit':
            layers = []
            gather_layers(layer_from_name(layer_name), layers)
            self.layers = order_by_bases(layers)
        else:
            self.layers = []
        count = 0
        for test in tests:
            count += test.countTestCases()
        self.count = count

    def testSetUp(self):
        """A layer may define a setup method to be called before each
        individual test.
        """
        for layer in self.layers:
            if hasattr(layer, 'testSetUp'):
                layer.testSetUp()

    def testTearDown(self):
        """A layer may define a teardown method to be called after each
           individual test.

           This is useful for clearing the state of global
           resources or resetting external systems such as relational
           databases or daemons.
        """
        for layer in self.layers[-1::-1]:
            if hasattr(layer, 'testTearDown'):
                layer.testTearDown()

    def startTest(self, test):
        self.testSetUp()
        unittest.TestResult.startTest(self, test)
        testsRun = self.testsRun - 1 # subtract the one the base class added
        count = test.countTestCases()
        self.testsRun = testsRun + count

        self.options.output.start_test(test, self.testsRun, self.count)

        self._threads = threading.enumerate()
        self._start_time = time.time()

    def addSuccess(self, test):
        t = max(time.time() - self._start_time, 0.0)
        self.options.output.test_success(test, t)

    def addError(self, test, exc_info):
        self.options.output.test_error(test, time.time() - self._start_time,
                                       exc_info)

        unittest.TestResult.addError(self, test, exc_info)

        if self.options.post_mortem:
            if self.options.resume_layer:
                self.options.output.error_with_banner("Can't post-mortem debug"
                                                      " when running a layer"
                                                      " as a subprocess!")
            else:
                post_mortem(exc_info)

    def addFailure(self, test, exc_info):
        self.options.output.test_failure(test, time.time() - self._start_time,
                                         exc_info)

        unittest.TestResult.addFailure(self, test, exc_info)

        if self.options.post_mortem:
            # XXX: mgedmin: why isn't there a resume_layer check here like
            # in addError?
            post_mortem(exc_info)

    def stopTest(self, test):
        self.testTearDown()
        self.options.output.stop_test(test)

        if gc.garbage:
            self.options.output.test_garbage(test, gc.garbage)
            # TODO: Perhaps eat the garbage here, so that the garbage isn't
            #       printed for every subsequent test.

        # Did the test leave any new threads behind?
        new_threads = [t for t in threading.enumerate()
                         if (t.isAlive()
                             and
                             t not in self._threads)]
        if new_threads:
            self.options.output.test_threads(test, new_threads)


def ordered_layers(tests_by_layer_name):
    layer_names = dict([(layer_from_name(layer_name), layer_name)
                        for layer_name in tests_by_layer_name])
    for layer in order_by_bases(layer_names):
        layer_name = layer_names[layer]
        yield layer_name, layer, tests_by_layer_name[layer_name]


def layer_from_name(layer_name):
    """Return the layer for the corresponding layer_name by discovering
       and importing the necessary module if necessary.

       Note that a name -> layer cache is maintained by name_from_layer
       to allow locating layers in cases where it would otherwise be
       impossible.
    """
    global _layer_name_cache
    if _layer_name_cache.has_key(layer_name):
        return _layer_name_cache[layer_name]
    layer_names = layer_name.split('.')
    layer_module, module_layer_name = layer_names[:-1], layer_names[-1]
    return getattr(import_name('.'.join(layer_module)), module_layer_name)


def order_by_bases(layers):
    """Order the layers from least to most specific (bottom to top)
    """
    named_layers = [(name_from_layer(layer), layer) for layer in layers]
    named_layers.sort()
    named_layers.reverse()
    gathered = []
    for name, layer in named_layers:
        gather_layers(layer, gathered)
    gathered.reverse()
    seen = {}
    result = []
    for layer in gathered:
        if layer not in seen:
            seen[layer] = 1
            if layer in layers:
                result.append(layer)
    return result


def gather_layers(layer, result):
    if layer is not object:
        result.append(layer)
    for b in layer.__bases__:
        gather_layers(b, result)


def post_mortem(exc_info):
    err = exc_info[1]
    if isinstance(err, (doctest.UnexpectedException, doctest.DocTestFailure)):

        if isinstance(err, doctest.UnexpectedException):
            exc_info = err.exc_info

            # Print out location info if the error was in a doctest
            if exc_info[2].tb_frame.f_code.co_filename == '<string>':
                print_doctest_location(err)

        else:
            print_doctest_location(err)
            # Hm, we have a DocTestFailure exception.  We need to
            # generate our own traceback
            try:
                exec ('raise ValueError'
                      '("Expected and actual output are different")'
                      ) in err.test.globs
            except:
                exc_info = sys.exc_info()

    print "%s:" % (exc_info[0], )
    print exc_info[1]
    pdb.post_mortem(exc_info[2])
    raise EndRun


def print_doctest_location(err):
    # This mimics pdb's output, which gives way cool results in emacs :)
    filename = err.test.filename
    if filename.endswith('.pyc'):
        filename = filename[:-1]
    print "> %s(%s)_()" % (filename, err.test.lineno+err.example.lineno+1)


class FakeInputContinueGenerator:

    def readline(self):
        print  'c\n'
        print '*'*70
        print ("Can't use pdb.set_trace when running a layer"
               " as a subprocess!")
        print '*'*70
        print
        return 'c\n'
