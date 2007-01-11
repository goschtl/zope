##############################################################################
#
# Copyright (c) 2006-2007 Zope Corporation and Contributors.
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
"""Zope 3 program entry points

The Zope 3 scripts, scriptzope, and debugzope are distributed
as templates, rather than as entry points. Here we provide entry-point
versions.

$Id$
"""

import os, sys

import zope.app.debug
import zope.app.twisted.main


def zglobals(args):
    db = zope.app.twisted.main.debug(args)
    if "PYTHONSTARTUP" in os.environ:
        execfile(os.environ["PYTHONSTARTUP"])

    app = zope.app.debug.Debugger.fromDatabase(db)
    return dict(
        app = app,
        debugger = app,
        root = app.root(),
        __name__ = '__main__',
        )

def script(args):
    globs = zglobals(args[:2])
    sys.argv[:] = args[2:]
    globs['__file__'] = sys.argv[0]
    execfile(sys.argv[0], globs)
    sys.exit()


banner = """Welcome to the Zope 3 debugging shell.

The application root object is available as the "root" variable.
A Zope debugger instance is available as the "debugger" (aka "app") variable.
"""

def debug(args):
    globs = zglobals(args)
    import code
    code.interact(banner=banner, local=globs)
