##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Import cycle detector.

This 

$Id$
"""
from zope.importtool import format
from zope.importtool import reporter


START = "<start>"
FINISH = "<finish>"
ERROR = "<error>"


class CyclicImportError(ImportError):

    def __init__(self, name, stack):
        ImportError.__init__(self, name)
        self.name = name
        self.stack = stack[:]

    def __str__(self):
        return ("disallowed cyclic import of %r; active imports are %r"
                % (self.name, self.stack[:-1]))


class CycleReporter(reporter.Reporter):

    def __init__(self):
        self.log = []
        self.stack = []

    def request(self, importer, name, fromlist):
        entry = [importer, None, START]
        self.log.append(entry)
        self.stack.append(entry)

    def found(self, importer, imported, fromlist):
        entry = self.stack.pop()
        entry[1] = imported
        self.log.append([importer, imported, FINISH])
        if not self.stack:
            self.check()
            self.log = []

    def check(self):
        stack = []
        for entry in self.log:
            importer, imported, event = entry
            if event == START:
                # If imported is None, an exception prevented the
                # import; we don't care about that case, but None can
                # be stack more than once, so we need to be careful.
                if imported is not None and imported in stack:
                    # report cycle
                    self.report_cycle(stack + [imported])
                stack.append(imported)
            else:
                assert event in FINISH, ERROR
                stack.pop()
        assert not stack

    def report_cycle(self, stack):
        raise CyclicImportError(stack[-1], stack)

    def display_report(self):
        pass


class CycleCollector(CycleReporter):

    def __init__(self):
        CycleReporter.__init__(self)
        self.cycles = {}

    def report_cycle(self, stack):
        t = tuple(stack)
        self.cycles[t] = self.cycles.get(t, 0) + 1

    def display_report(self):
        if self.cycles:
            cycles = self.cycles.keys()
            items = [(cycle[-1], ", ".join(cycle[:-1])) for cycle in cycles]
            items.sort()
            format.two_column_report(items)
        else:
            print "--------------------"
            print "No cycles to report."
