##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Extension to use doctest tests as unit tests

This module provides a DocTestSuite contructor for converting doctest
tests to unit tests.

$Id$
"""

from StringIO import StringIO
import doctest
import os
import pdb
import sys
import tempfile
import unittest


class DocTestTestCase(unittest.TestCase):
    """A test case that wraps a test function.

    This is useful for slipping pre-existing test functions into the
    PyUnit framework. Optionally, set-up and tidy-up functions can be
    supplied. As with TestCase, the tidy-up ('tearDown') function will
    always be called if the set-up ('setUp') function ran successfully.
    """

    def __init__(self, tester, name, doc, filename, lineno,
                 setUp=None, tearDown=None):
        unittest.TestCase.__init__(self)
        (self._dt_tester, self._dt_name, self._dt_doc,
         self._dt_filename, self._dt_lineno,
         self._dt_setUp, self._dt_tearDown
         ) = tester, name, doc, filename, lineno, setUp, tearDown

    def setUp(self):
        if self._dt_setUp is not None:
            self._dt_setUp()

    def tearDown(self):
        if self._dt_tearDown is not None:
            self._dt_tearDown()

    def setDebugModeOn(self):
        self._dt_tester.optionflags |= (
            doctest.RUN_DEBUGGER_ON_UNEXPECTED_EXCEPTION)

    def runTest(self):
        old = sys.stdout
        new = StringIO()
        try:
            sys.stdout = new
            failures, tries = self._dt_tester.runstring(
                self._dt_doc, self._dt_name)
        finally:
            sys.stdout = old

        if failures:
            raise self.failureException(self.format_failure(new.getvalue()))

    def format_failure(self, err):
        lineno = self._dt_lineno or "0 (don't know line no)"
        lname = '.'.join(self._dt_name.split('.')[-1:]) 
        return ('Failed doctest test for %s\n'
                '  File "%s", line %s, in %s\n\n%s'
                % (self._dt_name, self._dt_filename,
                   lineno, lname, err)
                )

    def id(self):
        return self._dt_name

    def __repr__(self):
        name = self._dt_name.split('.')
        return "%s (%s)" % (name[-1], '.'.join(name[:-1]))

    __str__ = __repr__

    def shortDescription(self):
        return "Doctest: " + self._dt_name

class DocTestFileTestCase(DocTestTestCase):

    def id(self):
        return '_'.join(self._dt_name.split('.'))

    def __repr__(self):
        return self._dt_filename 
    __str__ = __repr__

    def format_failure(self, err):
        return ('Failed doctest test for %s\n  File "%s", line 0\n\n%s'
                % (self._dt_name, self._dt_filename, err)
                )

def DocFileTest(path, package=None, globs=None,
                setUp=None, tearDown=None,
                ):
    
    package = _normalizeModule(package)
    name = path.split('/')[-1]
    dir = os.path.dirname(package.__file__)
    path = os.path.join(dir, *(path.split('/')))
    doc = open(path).read()
    tester = doctest.Tester(globs=(globs or {}))
    return DocTestFileTestCase(tester, name, doc, path, 0, setUp, tearDown)

def DocFileSuite(*paths, **kw):
    """Creates a suite of doctest files.

    One or more text file paths are given as strings.  These should
    use "/" characters to separate path segments.  Paths are relative
    to the directory of the calling module, or relative to the package
    passed as a keyword argument.

    A number of options may be provided as keyword arguments:

    package
      The name of a Python package. Text-file paths will be
      interpreted relative to the directory containing this package.
      The package may be supplied as a package object or as a dotted
      package name.

    setUp
      The name of a set-up function. This is called before running the
      tests in each file.

    tearDown
      The name of a tear-down function. This is called after running the
      tests in each file.

    globs
      A dictionary containing initial global variables for the tests.
    """
    # BBB temporarily support passing package as first argument
    if not isinstance(paths[0], basestring):
        import warnings
        warnings.warn("DocFileSuite package argument must be provided as a "
                      "keyword argument",
                      DeprecationWarning, 2)
        kw = kw.copy()
        kw['package'] = paths[0]
        paths = paths[1:]
    else:
        kw['package'] = _normalizeModule(kw.get('package'))
    
    suite = unittest.TestSuite()
    for path in paths:
        suite.addTest(DocFileTest(path, **kw))
    return suite

def DocTestSuite(module=None,
                 setUp=lambda: None,
                 tearDown=lambda: None,
                 ):
    """Convert doctest tests for a mudule to a unittest test suite

    This tests convers each documentation string in a module that
    contains doctest tests to a unittest test case. If any of the
    tests in a doc string fail, then the test case fails. An error is
    raised showing the name of the file containing the test and a
    (sometimes approximate) line number.

    A module argument provides the module to be tested. The argument
    can be either a module or a module name.

    If no argument is given, the calling module is used.

    """
    module = _normalizeModule(module)
    tests = _findTests(module)

    if not tests:
        raise ValueError(module, "has no tests")

    tests.sort()
    suite = unittest.TestSuite()
    tester = doctest.Tester(module)
    for name, doc, filename, lineno in tests:
        if not filename:
            filename = module.__file__
            if filename.endswith(".pyc"):
                filename = filename[:-1]
            elif filename.endswith(".pyo"):
                filename = filename[:-1]

        suite.addTest(DocTestTestCase(
            tester, name, doc, filename, lineno,
            setUp, tearDown))


    return suite

def _normalizeModule(module):
    # Normalize a module
    if module is None:
        # Test the calling module
        module = sys._getframe(2).f_globals['__name__']
        module = sys.modules[module]

    elif isinstance(module, (str, unicode)):
        module = __import__(module, globals(), locals(), ["*"])

    return module

def _doc(name, object, tests, prefix, filename='', lineno=''):
    doc = getattr(object, '__doc__', '')
    if doc and doc.find('>>>') >= 0:
        tests.append((prefix+name, doc, filename, lineno))


def _findTests(module, prefix=None):
    if prefix is None:
        prefix = module.__name__
    dict = module.__dict__
    tests = []
    _doc(prefix, module, tests, '',
         lineno="1 (or below)")
    prefix = prefix and (prefix + ".")
    _find(dict.items(), module, dict, tests, prefix)
    return tests

def _find(items, module, dict, tests, prefix, minlineno=0):
    for name, object in items:

        # Only interested in named objects
        if not hasattr(object, '__name__'):
            continue

        if hasattr(object, 'func_globals'):
            # Looks like a func
            if object.func_globals is not dict:
                # Non-local func
                continue
            code = getattr(object, 'func_code', None)
            filename = getattr(code, 'co_filename', '')
            lineno = getattr(code, 'co_firstlineno', -1) + 1
            if minlineno:
                minlineno = min(lineno, minlineno)
            else:
                minlineno = lineno
            _doc(name, object, tests, prefix, filename, lineno)

        elif hasattr(object, "__module__"):
            # Maybe a class-like things. In which case, we care
            if object.__module__ != module.__name__:
                continue # not the same module
            if not (hasattr(object, '__dict__')
                    and hasattr(object, '__bases__')):
                continue # not a class

            lineno = _find(object.__dict__.items(), module, dict, tests,
                           prefix+name+".")

            _doc(name, object, tests, prefix,
                 lineno="%s (or above)" % (lineno-3))

    return minlineno




####################################################################
# doctest debugger

def invert_src(s):
    """Invert a doctest

    Examples become regular code. Everything else becomes comments    
    """
    isPS1, isPS2 = doctest._isPS1, doctest._isPS2
    isEmpty, isComment = doctest._isEmpty, doctest._isComment
    output = []
    lines = s.split("\n")
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        i = i + 1
        m = isPS1(line)
        if m is None:
            output.append('#  '+line)
            continue
        j = m.end(0)  # beyond the prompt
        if isEmpty(line, j) or isComment(line, j):
            # a bare prompt or comment -- not interesting
            output.append('#  '+line[j:])

        lineno = i - 1
        if line[j] != " ":
            raise ValueError("line %r of docstring lacks blank after %s: %s" %
                             (lineno, PS1, line))
        j = j + 1
        blanks = m.group(1)
        nblanks = len(blanks)
        # suck up this and following PS2 lines
        while 1:
            output.append(line[j:])
            line = lines[i]
            m = isPS2(line)
            if m:
                if m.group(1) != blanks:
                    raise ValueError("inconsistent leading whitespace "
                        "in line %r of docstring: %s" % (i, line))
                i = i + 1
            else:
                break

        # suck up response
        if not (isPS1(line) or isEmpty(line)):
            while 1:
                if line[:nblanks] != blanks:
                    raise ValueError("inconsistent leading whitespace "
                        "in line %r of docstring: %s" % (i, line))
                output.append('#'+line[nblanks:])
                i = i + 1
                line = lines[i]
                if isPS1(line) or isEmpty(line):
                    break

    return '\n'.join(output)


def testsource(module, name):
    """Extract the test sources from a doctest test docstring as a script

    Provide the module (or dotted name of the module) containing the
    test to be debugged and the name (within the module) of the object
    with the doc string with tests to be debugged.

    """
    module = _normalizeModule(module)
    tests = _findTests(module, "")
    test = [doc for (tname, doc, f, l) in tests if tname == name]
    if not test:
        raise ValueError(name, "not found in tests")
    return invert_src(test[0])

def debug_src(src, pm=False, globs=None):
    """Debug a single doctest test doc string

    The string is provided directly
    """

    src = invert_src(src)
    debug_script(src, pm, globs)

def debug_script(src, pm=False, globs=None):
    "Debug a test script"
    srcfilename = tempfile.mktemp("doctestdebug.py")
    open(srcfilename, 'w').write(src)
    if globs:
        globs = globs.copy()
    else:
        globs = {}

    try:
        if pm:
            try:
                execfile(srcfilename, globs, globs)
            except:
                print sys.exc_info()[1]
                pdb.post_mortem(sys.exc_info()[2])
        else:
            # Note that %r is vital here.  '%s' instead can, e.g., cause
            # backslashes to get treated as metacharacters on Windows.
            pdb.run("execfile(%r)" % srcfilename, globs, globs)
    finally:
        os.remove(srcfilename)

def debug(module, name, pm=False):
    """Debug a single doctest test doc string

    Provide the module (or dotted name of the module) containing the
    test to be debugged and the name (within the module) of the object
    with the doc string with tests to be debugged.

    """
    module = _normalizeModule(module)
    testsrc = testsource(module, name)
    debug_script(testsrc, pm, module.__dict__)
