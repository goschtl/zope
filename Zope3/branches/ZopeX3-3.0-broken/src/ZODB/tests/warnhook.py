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
import warnings

class WarningsHook:
    """Hook to capture warnings generated by Python.

    The function warnings.showwarning() is designed to be hooked by
    application code, allowing the application to customize the way it
    handles warnings.

    This hook captures the unformatted warning information and stored
    it in a list.  A test can inspect this list after the test is over.

    Issues:

    The warnings module has lots of delicate internal state.  If
    a warning has been reported once, it won't be reported again.  It
    may be necessary to extend this class with a mechanism for
    modifying the internal state so that we can be guaranteed a
    warning will be reported.

    If Python is run with a warnings filter, e.g. python -Werror,
    then a test that is trying to inspect a particular warning will
    fail.  Perhaps this class can be extended to install more-specific
    filters the test to work anyway.
    """

    def __init__(self):
        self.original = None
        self.warnings = []

    def install(self):
        self.original = warnings.showwarning
        warnings.showwarning = self.showwarning

    def uninstall(self):
        assert self.original is not None
        warnings.showwarning = self.original
        self.original = None

    def showwarning(self, message, category, filename, lineno):
        self.warnings.append((str(message), category, filename, lineno))

    def clear(self):
        self.warnings = []
