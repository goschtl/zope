##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Command-line tool to perform import analysis.
"""
import optparse
import os
import sys

from zope.importtool import hook
from zope.importtool import reporter


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        options = Options(argv)
    except SystemExit:
        print >>sys.stderr, "usage: %s script [args]"
        raise
    run(options)


def run(options):
    reporter = FirstImportReporter()
    hook.install_reporter(reporter)
    globals = {"__name__": "__main__",
               "__file__": options.argv[0]}
    old_argv = sys.argv[:]
    sys.argv[:] = options.argv
    try:
        execfile(options.script, globals)
    finally:
        hook.uninstall_reporter()
        sys.argv[:] = old_argv
    reporter.display_report()


class Options:

    def __init__(self, argv):
        self.program = os.path.basename(argv[0])
        if len(argv) < 2:
            raise SystemExit(2)
        self.argv = argv[1:]
        self.script = self.argv[0]


class FirstImportReporter(reporter.Reporter):

    def __init__(self):
        self.already_found = {}
        self.index = 0

    def found(self, importer, imported, fromlist):
        if imported not in self.already_found:
            self.already_found[imported] = importer, self.index
            self.index += 1

    def display_report(self):
        L = [(i, imported, importer)
             for imported, (importer, i) in self.already_found.iteritems()]
        L.sort()
        if not L:
            print "---------------------"
            print "No imports to report."
        else:
            left_width = right_width = 0
            for i, imported, importer in L:
                left_width = max(left_width, len(imported))
                right_width = max(right_width, len(importer))
            width = left_width + 1 + right_width
            print width * "-"
            for i, imported, importer in L:
                print imported.ljust(left_width), importer
