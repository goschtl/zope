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
"""Code coverage analysis

$Id: __init__.py 86218 2008-05-03 14:17:26Z ctheune $
"""

import trace
import sys
import os.path
import threading


# For some reason, the doctest module resets the trace callable randomly, thus
# disabling the coverage. Simply disallow the code from doing this. A real
# trace can be set, so that debugging still works.
osettrace = sys.settrace
def settrace(trace):
    if trace is None:
        return
    osettrace(trace)


class TestTrace(trace.Trace):
    """Simple tracer.

    >>> tracer = TestTrace([], count=False, trace=False)

    Simple rules for use: you can't stop the tracer if it not started
    and you can't start the tracer if it already started:

    >>> tracer.stop()
    Traceback (most recent call last):
        File 'testrunner.py'
    AssertionError: can't stop if not started

    >>> tracer.start()
    >>> tracer.start()
    Traceback (most recent call last):
        File 'testrunner.py'
    AssertionError: can't start if already started

    >>> tracer.stop()
    >>> tracer.stop()
    Traceback (most recent call last):
        File 'testrunner.py'
    AssertionError: can't stop if not started
    """

    def __init__(self, directories, **kw):
        trace.Trace.__init__(self, **kw)
        self.ignore = TestIgnore(directories)
        self.started = False

    def start(self):
        assert not self.started, "can't start if already started"
        if not self.donothing:
            sys.settrace = settrace
            sys.settrace(self.globaltrace)
            threading.settrace(self.globaltrace)
        self.started = True

    def stop(self):
        assert self.started, "can't stop if not started"
        if not self.donothing:
            sys.settrace = osettrace
            sys.settrace(None)
            threading.settrace(None)
        self.started = False


class TestIgnore:

    def __init__(self, directories):
        self._test_dirs = [self._filenameFormat(d[0]) + os.path.sep
                           for d in directories]
        self._ignore = {}
        self._ignored = self._ignore.get

    def names(self, filename, modulename):
        # Special case: Modules generated from text files; i.e. doctests
        if modulename == '<string>':
            return True
        filename = self._filenameFormat(filename)
        ignore = self._ignored(filename)
        if ignore is None:
            ignore = True
            if filename is not None:
                for d in self._test_dirs:
                    if filename.startswith(d):
                        ignore = False
                        break
            self._ignore[filename] = ignore
        return ignore

    def _filenameFormat(self, filename):
        return os.path.abspath(filename)

if sys.platform == 'win32':
    #on win32 drive name can be passed with different case to `names`
    #that lets e.g. the coverage profiler skip complete files
    #_filenameFormat will make sure that all drive and filenames get lowercased
    #albeit trace coverage has still problems with lowercase drive letters
    #when determining the dotted module name
    OldTestIgnore = TestIgnore

    class TestIgnore(OldTestIgnore):
        def _filenameFormat(self, filename):
            return os.path.normcase(os.path.abspath(filename))
