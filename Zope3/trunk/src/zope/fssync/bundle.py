##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Zope 3 bundle management utility.

Command line syntax summary:

%(program)s create PATH ...

``%(program)s help'' prints the global help (this message)
``%(program)s help command'' prints the local help for the command
"""
"""
$Id: bundle.py,v 1.1 2003/08/12 22:08:34 fdrake Exp $
"""

import os

from zope.fssync.command import Command, Usage
from zope.fssync.fsbundle import FSBundle


def main():
    """Main program.

    The return value is the suggested sys.exit() status code:
    0 or None for success
    2 for command line syntax errors
    1 or other for later errors
    """
    cmd = Command(usage=__doc__)
    for func, aliases, short, long in command_table:
        cmd.addCommand(func.__name__, func, short, long, aliases)

    return cmd.main()


def create(opts, args):
    """%(program)s create PATH ...

    """
    factory = None
    type = None
    for opt, arg in opts:
        if opt in ("-f", "--factory"):
            if factory:
                raise Usage("-f/--factory can only be given once")
            factory = arg
        elif opt in ("-t", "--type"):
            if type:
                raise Usage("-t/--type can only be given once")
            type = arg
    if len(args) != 1:
        raise Usage("create requires exactly one path")
    fs = FSBundle()
    fs.create(args[0], type, factory)


command_table = [
    # name is taken from the function name
    # function, aliases,  short opts,   long opts
    (create,    "",       "f:t:",       "factory= type="),
    ]
