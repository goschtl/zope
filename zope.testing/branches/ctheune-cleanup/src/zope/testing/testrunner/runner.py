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

import cStringIO
import gc
import glob
import logging
import os
import pdb
import sys
import tempfile
import threading
import time
import traceback
import unittest

from zope.testing import doctest
from zope.testing.testrunner.profiling import available_profilers
from zope.testing.testrunner.find import find_tests, test_dirs
from zope.testing.testrunner.find import StartUpFailure, import_name
from zope.testing.testrunner.find import name_from_layer, _layer_name_cache
from zope.testing.testrunner.coverage import TestTrace
from zope.testing.testrunner.refcount import TrackRefs
from zope.testing.testrunner.options import get_options

real_pdb_set_trace = pdb.set_trace


class SubprocessError(Exception):
    """An error occurred when running a subprocess
    """

    def __str__(self):
        return self.args


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

    def run(self):
        self.configure()
        self.setup_features()
        self.shutdown_features()

        # Set the default logging policy.
        # XXX There are no tests for this logging behavior.
        # It's not at all clear that the test runner should be doing this.
        configure_logging()

        # Control reporting flags during run
        old_reporting_flags = doctest.set_unittest_reportflags(0)

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
        if options.fail:
            return True

        output = options.output

        options.testrunner_defaults = self.defaults
        options.resume_layer = resume_layer
        options.resume_number = resume_number

        # Make sure we start with real pdb.set_trace.  This is needed
        # to make tests of the test runner work properly. :)
        pdb.set_trace = real_pdb_set_trace

        if (options.profile
            and sys.version_info[:3] <= (2,4,1)
            and __debug__):
            output.error('Because of a bug in Python < 2.4.1, profiling '
                         'during tests requires the -O option be passed to '
                         'Python (not the test runner).')
            sys.exit()

        if options.coverage:
            tracer = TestTrace(test_dirs(options, {}), trace=False, count=True)
            tracer.start()
        else:
            tracer = None

        if options.profile:
            prof_prefix = 'tests_profile.'
            prof_suffix = '.prof'
            prof_glob = prof_prefix + '*' + prof_suffix

            # if we are going to be profiling, and this isn't a subprocess,
            # clean up any stale results files
            if not options.resume_layer:
                for file_name in glob.glob(prof_glob):
                    os.unlink(file_name)

            # set up the output file
            oshandle, file_path = tempfile.mkstemp(prof_suffix, prof_prefix, '.')
            profiler = available_profilers[options.profile](file_path)
            profiler.enable()

        try:
            try:
                self.options = options
                self.find_tests()
                failed = self.run_tests()
            except EndRun:
                failed = True
        finally:
            if tracer:
                tracer.stop()
            if options.profile:
                profiler.disable()
                profiler.finish()
                # We must explicitly close the handle mkstemp returned, else on
                # Windows this dies the next time around just above due to an
                # attempt to unlink a still-open file.
                os.close(oshandle)

        if options.profile and not options.resume_layer:
            stats = profiler.loadStats(prof_glob)
            stats.sort_stats('cumulative', 'calls')
            output.profiler_stats(stats)

        if tracer:
            coverdir = os.path.join(os.getcwd(), options.coverage)
            r = tracer.results()
            r.write_results(summary=True, coverdir=coverdir)

        doctest.set_unittest_reportflags(old_reporting_flags)

        if failed and options.exitwithstatus:
            sys.exit(1)

        return failed

    def configure(self):
        if self.args is None:
            self.args = sys.argv[:]

    def setup_features(self):
        pass

    def find_tests(self):
        pass

    def run_tests(self):
        """Find and run tests

        Passing a list of suites using the found_suites parameter will cause
        that list of suites to be used instead of attempting to load them from
        the filesystem. This is useful for unit testing the test runner.

        Returns True if there where failures or False if all tests passed.

        """
        options = self.options
        found_suites = self.found_suites

        global _layer_name_cache
        _layer_name_cache.clear() # Reset to enforce test isolation

        output = options.output

        if options.resume_layer:
            original_stderr = sys.stderr
            sys.stderr = sys.stdout
        elif options.verbose:
            if options.all:
                msg = "Running tests at all levels"
            else:
                msg = "Running tests at level %d" % options.at_level
            output.info(msg)

        old_threshold = gc.get_threshold()
        if options.gc:
            if len(options.gc) > 3:
                output.error("Too many --gc options")
                sys.exit(1)
            if options.gc[0]:
                output.info("Cyclic garbage collection threshold set to: %s" %
                            repr(tuple(options.gc)))
            else:
                output.info("Cyclic garbage collection is disabled.")

            gc.set_threshold(*options.gc)

        old_flags = gc.get_debug()
        if options.gc_option:
            new_flags = 0
            for op in options.gc_option:
                new_flags |= getattr(gc, op)
            gc.set_debug(new_flags)

        old_reporting_flags = doctest.set_unittest_reportflags(0)
        reporting_flags = 0
        if options.ndiff:
            reporting_flags = doctest.REPORT_NDIFF
        if options.udiff:
            if reporting_flags:
                output.error("Can only give one of --ndiff, --udiff, or --cdiff")
                sys.exit(1)
            reporting_flags = doctest.REPORT_UDIFF
        if options.cdiff:
            if reporting_flags:
                output.error("Can only give one of --ndiff, --udiff, or --cdiff")
                sys.exit(1)
            reporting_flags = doctest.REPORT_CDIFF
        if options.report_only_first_failure:
            reporting_flags |= doctest.REPORT_ONLY_FIRST_FAILURE

        if reporting_flags:
            doctest.set_unittest_reportflags(reporting_flags)
        else:
            doctest.set_unittest_reportflags(old_reporting_flags)


        # Add directories to the path
        for path in options.path:
            if path not in sys.path:
                sys.path.append(path)

        tests_by_layer_name = find_tests(options, found_suites)

        ran = 0
        failures = []
        errors = []
        nlayers = 0
        import_errors = tests_by_layer_name.pop(None, None)

        output.import_errors(import_errors)

        if 'unit' in tests_by_layer_name:
            tests = tests_by_layer_name.pop('unit')
            if (not options.non_unit) and not options.resume_layer:
                if options.layer:
                    should_run = False
                    for pat in options.layer:
                        if pat('unit'):
                            should_run = True
                            break
                else:
                    should_run = True

                if should_run:
                    if options.list_tests:
                        output.list_of_tests(tests, 'unit')
                    else:
                        output.info("Running unit tests:")
                        nlayers += 1
                        ran += run_tests(options, tests, 'unit', failures, errors)

        setup_layers = {}

        layers_to_run = list(ordered_layers(tests_by_layer_name))
        if options.resume_layer is not None:
            layers_to_run = [
                (layer_name, layer, tests)
                for (layer_name, layer, tests) in layers_to_run
                if layer_name == options.resume_layer
            ]
        elif options.layer:
            layers_to_run = [
                (layer_name, layer, tests)
                for (layer_name, layer, tests) in layers_to_run
                if filter(None, [pat(layer_name) for pat in options.layer])
            ]


        if options.list_tests:
            for layer_name, layer, tests in layers_to_run:
                output.list_of_tests(tests, layer_name)
            return False

        start_time = time.time()

        for layer_name, layer, tests in layers_to_run:
            nlayers += 1
            try:
                ran += run_layer(options, layer_name, layer, tests,
                                 setup_layers, failures, errors)
            except CanNotTearDown:
                setup_layers = None
                if not options.resume_layer:
                    ran += resume_tests(options, layer_name, layers_to_run,
                                        failures, errors)
                    break

        if setup_layers:
            if options.resume_layer == None:
                output.info("Tearing down left over layers:")
            tear_down_unneeded(options, (), setup_layers, True)

        total_time = time.time() - start_time

        if options.resume_layer:
            sys.stdout.close()
            # Communicate with the parent.  The protocol is obvious:
            print >> original_stderr, ran, len(failures), len(errors)
            for test, exc_info in failures:
                print >> original_stderr, ' '.join(str(test).strip().split('\n'))
            for test, exc_info in errors:
                print >> original_stderr, ' '.join(str(test).strip().split('\n'))

        else:
            if options.verbose:
                output.tests_with_errors(errors)
                output.tests_with_failures(failures)

            if nlayers != 1:
                output.totals(ran, len(failures), len(errors), total_time)

            output.modules_with_import_problems(import_errors)

        doctest.set_unittest_reportflags(old_reporting_flags)

        if options.gc_option:
            gc.set_debug(old_flags)

        if options.gc:
            gc.set_threshold(*old_threshold)

        return bool(import_errors or failures or errors)

    def shutdown_features(self):
        pass


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
            raise SubprocessError(line+suberr.read())

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

def configure_logging():
    """Initialize the logging module."""
    import logging.config

    # Get the log.ini file from the current directory instead of
    # possibly buried in the build directory.  TODO: This isn't
    # perfect because if log.ini specifies a log file, it'll be
    # relative to the build directory.  Hmm...  logini =
    # os.path.abspath("log.ini")

    logini = os.path.abspath("log.ini")
    if os.path.exists(logini):
        logging.config.fileConfig(logini)
    else:
        # If there's no log.ini, cause the logging package to be
        # silent during testing.
        root = logging.getLogger()
        root.addHandler(NullHandler())
        logging.basicConfig()

    if os.environ.has_key("LOGGING"):
        level = int(os.environ["LOGGING"])
        logging.getLogger().setLevel(level)


class NullHandler(logging.Handler):
    """Logging handler that drops everything on the floor.

    We require silence in the test environment.  Hush.
    """

    def emit(self, record):
        pass


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


