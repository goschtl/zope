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
    h = hook.ReportingHook(options.reporter)
    h.install()
    globals = {"__name__": "__main__",
               "__file__": options.argv[0]}
    old_argv = sys.argv[:]
    sys.argv[:] = options.argv
    try:
        execfile(options.script, globals)
    finally:
        h.uninstall()
        sys.argv[:] = old_argv
    options.reporter.display_report()


class Options:

    known_options = ["--first-import", "--cyclic-imports"]

    def __init__(self, argv):
        self.program = os.path.basename(argv[0])
        self.argv = argv[1:]
        self.reporter = None
        while self.argv and self.argv[0] in self.known_options:
            opt = self.argv.pop(0)
            m = getattr(self, opt[2:].replace("-", "_"))
            m()
        if len(argv) < 2:
            raise SystemExit(2)
        self.script = self.argv[0]
        if self.reporter is None:
            self.reporter = FirstImportReporter()

    def first_import(self):
        if self.reporter is not None:
            raise SystemExit(2)
        self.reporter = FirstImportReporter()

    def cyclic_imports(self):
        if self.reporter is not None:
            raise SystemExit(2)
        from zope.importtool import cycle
        self.reporter = cycle.CycleReporter()


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
