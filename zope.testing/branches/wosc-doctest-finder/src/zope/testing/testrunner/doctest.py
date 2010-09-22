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
"""Doc test support for the test runner.

$Id: __init__.py 86232 2008-05-03 15:09:33Z ctheune $
"""

from zope.testing import doctest
from zope.testing.testrunner.find import (
    name_from_layer, test_dirs, walk_with_symlinks)
import os.path
import re
import zope.dottedname.resolve
import zope.testing.testrunner.feature
import zope.testing.testrunner.layer


class DocTest(zope.testing.testrunner.feature.Feature):

    active = True

    def global_setup(self):
        options = self.runner.options

        self.old_reporting_flags = doctest.set_unittest_reportflags(0)

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

    def global_shutdown(self):
        doctest.set_unittest_reportflags(self.old_reporting_flags)


class DocFileFind(zope.testing.testrunner.feature.Feature):
    """Finds doctest files and registers them with the test runner."""

    active = True

    def global_setup(self):
        unittest_layer = name_from_layer(
            zope.testing.testrunner.layer.UnitTests)
        tests = {}
        for (package, testfile, factory) in self._find_doctest_files():
            test = factory(testfile, package=package)
            layer = getattr(test, 'layer', unittest_layer)
            tests[layer] = test
        self.runner.register_tests(tests)

    def _find_doctest_files(self):
        options = self.runner.options

        for (path, given_package) in test_dirs(options, {}):
            for dirname, dirs, files in walk_with_symlinks(options, path):
                if given_package:
                    package = given_package
                else:
                    package = dirname.replace(path + os.path.sep, '')
                    package = package.replace(os.path.sep, '.')

                for f in files:
                    if options.doctests_pattern(f):
                        f = os.path.join(dirname, f)
                        factory = parse_directive_from_file('testcase', f)
                        if not factory:
                            continue
                        factory = zope.dottedname.resolve.resolve(factory)
                        yield (package, f, factory)


def parse_directive_from_string(directive, text):
    """Looks for a reST directive in a string.

    Returns the found value or `None`. A directive has the form::

     .. <directive>:: <value>
    """

    directive_pattern = re.compile(
        r'^(\.\.\s+)%s\s*::(.*)$' % (directive,), re.IGNORECASE)
    for line in text.split('\n'):
        line = line.strip()
        result = directive_pattern.match(line)
        if result is None:
            continue
        result = result.groups()[1].strip()
        return unicode(result)
    return None


def parse_directive_from_file(directive, filepath):
    """Looks for a reST directive in a file. (see `parse_directive_from_string`)
    """

    return parse_directive_from_string(directive, open(filepath, 'rb').read())
