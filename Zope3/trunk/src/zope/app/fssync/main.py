##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Zope 3 bundle management utility.

Command line syntax summary:

%(program)s create BUNDLE SOURCE
%(program)s unpack BUNDLE TARGET

``%(program)s help'' prints the global help (this message)
``%(program)s help command'' prints the local help for the command
"""
"""
$Id$
"""
__docformat__ = 'restructuredtext'

from zope.fssync.command import Command, Usage

from zope.app.fssync.fsbundle import FSBundle


def main():
    """Main program.

    The return value is the suggested `sys.exit()` status code:
    ``0`` or ``None`` for success
    ``2`` for command line syntax errors
    ``1`` or other for later errors
    """
    cmd = Command(usage=__doc__)
    for func, aliases, short, long in command_table:
        cmd.addCommand(func.__name__, func, short, long, aliases)

    return cmd.main()


def create(opts, args):
    """%(program)s create BUNDLE SOURCE

    Create a bundle from a site management folder or another bundle.
    The bundle will only be created if the container is a site
    management folder.  BUNDLE must be a valid bundle name.

    The contents of SOURCE are copied into the newly created bundle,
    and are scheduled for addition to the database.  The new bundle
    can be manipulated using ``zsync add`` and ``zsync revert`` (and just
    editing the contents) as needed before committing it to the
    database.
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
    source = None
    if len(args) == 1:
        path = args[0]
    elif len(args) == 2:
        path, source = args
    else:
        raise Usage("create requires exactly one path")
    fs = FSBundle()
    fs.create(path, type, factory, source)


def unpack(opts, args):
    """%(program)s unpack bundle [dest]

    
    """
    if len(args) < 1:
        raise Usage("unpack requires a bundle")
    if len(args) > 2:
        raise Usage("unpack allows at most two args")
    source = args[0]
    if len(args) == 1:
        target = os.curdir
    else:
        target = args[1]
    fs = FSBundle()
    fs.unpack(source, target)


command_table = [
    # name is taken from the function name
    # function, aliases,  short opts,   long opts
    (create,    "",       "f:t:",       "factory= type="),
    (unpack,    "",       "",           ""),
    ]
