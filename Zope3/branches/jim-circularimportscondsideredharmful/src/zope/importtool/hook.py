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
"""Low-level hook for __import__.

This allows a 'reporter' function to be installed that can report what
imports have occurred, possibly taking some action to block the import
(by raising an exception).

The reporter function is called with four arguments:

- the full name of the module performing the import,
- the full name of the module that was imported,
- the name by which the importer referenced the imported module (this
  may be a relative name rather than a full name), and
- the 'fromlist' argument passed to __import__().

$Id$
"""

import __builtin__
import sys


class ReportingHook:

    def __init__(self, reporter):
        self.reporter = reporter
        self.active = False
        self.previous = None

    def install(self):
        if self.active:
            raise RuntimeError("import reporting hook already installed")
        self.previous = __import__
        __builtin__.__import__ = self.importhook
        self.active = True

    def uninstall(self):
        if not self.active:
            raise RuntimeError("import reporting hook not installed")
        if __import__ != self.importhook:
            raise RuntimeError("someone else is controlling imports: %r"
                               % __import__)
        __builtin__.__import__ = self.previous
        self.active = False
        self.previous = None

    def reset(self):
        # reset as best we can; this is really for use from tests
        if self.previous is not None:
            __builtin__.__import__ = self.previous
            self.previous = None
        self.active = False

    def importhook(self, name, globals=None, locals=None, fromlist=None):
        if globals is None:
            globals = sys._getframe(1).f_globals
        importer = globals.get("__name__")
        self.reporter.request(importer, name, fromlist)
        try:
            v = self.previous(name, globals, locals, fromlist)
        except:
            self.reporter.exception(importer, name, fromlist,
                                    sys.exc_info())
            raise
        if fromlist:
            imported = getattr(v, "__name__", None)
        else:
            mod = self.previous(name, globals, locals, ("foo",))
            imported = getattr(mod, "__name__", None)
        self.reporter.found(importer, imported, fromlist)
        return v
