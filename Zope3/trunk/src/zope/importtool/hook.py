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

__all__ = "install_reporter", "uninstall_reporter"


previous__import__ = None
current__import__ = None


def install_reporter(reporter):
    global current__import__
    global previous__import__
    if previous__import__ is not None:
        raise RuntimeError("import reporting hook already installed")

    def importhook(name, globals, locals, fromlist):
        importer = globals.get("__name__")
        reporter.request(importer, name, fromlist)
        v = previous__import__(name, globals, locals, fromlist)
        if fromlist:
            imported = getattr(v, "__name__", None)
        else:
            mod = previous__import__(name, globals, locals, ("foo",))
            imported = getattr(mod, "__name__", None)
        reporter.found(importer, imported, fromlist)
        return v

    previous__import__ = __builtin__.__import__
    __builtin__.__import__ = importhook
    current__import__ = importhook


def uninstall_reporter():
    if __builtin__.__import__ is not current__import__:
        raise RuntimeError("someone else is controlling imports")
    reset()


def active():
    return current__import__ is not None


def reset():
    # reset as best we can; this is really for use from tests
    global current__import__
    global previous__import__
    if previous__import__ is not None:
        __builtin__.__import__ = previous__import__
        previous__import__ = None
    current__import__ = None
