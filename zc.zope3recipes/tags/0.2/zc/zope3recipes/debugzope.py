##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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

$Id$
"""

import os, sys, traceback
import zope.app.debug
import zope.app.twisted.main
import zope.app.appsetup.interfaces
from zope.event import notify


def load_options(args):
    options = zope.app.twisted.main.ZopeOptions()
    options.schemadir = os.path.dirname(os.path.abspath(
        zope.app.twisted.main.__file__))
    options.positional_args_allowed = True
    options.realize(args)

    if options.configroot.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.configroot.path]
    return options


def zglobals(options):
    zope.app.appsetup.config(options.site_definition)
    db = zope.app.appsetup.appsetup.multi_database(options.databases)[0][0]
    notify(zope.app.appsetup.interfaces.DatabaseOpened(db))
    
    if "PYTHONSTARTUP" in os.environ:
        execfile(os.environ["PYTHONSTARTUP"])
    
    app = zope.app.debug.Debugger.fromDatabase(db)
    return dict(
        app = app,
        debugger = app,
        root = app.root(),
        __name__ = '__main__',
        )

def debug(args=None):
    if args is None:
        args = sys.argv[1:]

    options = load_options(args)
    try:
        globs = zglobals(options.configroot)
    except:
        if options.args:
            raise
        else:
            traceback.print_exc()
            import pdb
            pdb.post_mortem(sys.exc_info()[2])
            return
            
            
    args = options.args

    if args:
        sys.argv[:] = args
        globs['__file__'] = sys.argv[0]
        execfile(sys.argv[0], globs)
        sys.exit()
    else:
        import code
        code.interact(banner=banner, local=globs)

banner = """Welcome to the Zope 3 "debugger".
The application root object is available as the root variable.
A Zope debugger instance is available as the debugger (aka app) variable.
"""
