#! /usr/bin/env python
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
"""Filesystem synchronization utility for Zope 3.

Command line syntax summary:

fssync [global_options] checkout [local_options] URL [TARGETDIR]
fssync [global_options] update [local_options] [TARGET ...]
fssync [global_options] commit [local_options] [TARGET ...]
fssync [global_options] diff [local_options] [TARGET ...]
fssync [global_options] add [local_options] TARGET ...
fssync [global_options] remove [local_options] TARGET ...

For now, the only global option is -h/--help; there are no local
options yet except for diff, which supports a small subset of the
options of GNU diff.

$Id: main.py,v 1.8 2003/05/13 21:16:22 gvanrossum Exp $
"""

import os
import sys
import getopt

from os.path import dirname, join, realpath

# Find the zope root directory.
# XXX This assumes this script is <root>/src/zope/fssync/sync.py
scriptfile = sys.argv[0]
scriptdir = realpath(dirname(scriptfile))
rootdir = dirname(dirname(dirname(scriptdir)))

# Hack to fix the module search path
try:
    import zope.fssync
    # All is well
except ImportError:
    # Fix the path to include <root>/src
    srcdir = join(rootdir, "src")
    sys.path.append(srcdir)

from zope.fssync.fssync import Error, FSSync

class Usage(Error):
    """Subclass for usage error (command-line syntax).

    You should return an exit status of 2 rather than 1 when catching this.
    """

def main(argv=None):
    """Main program.

    You can pass it an argument list (which must include the command
    name as argv[0]); it defaults to sys.argv.

    The return value is the suggested sys.exit() status code:
    0 or None for success
    2 for command line syntax errors
    1 or other for later errors
    """
    try:
        if argv is None:
            argv = sys.argv

        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage("global option error: %s", msg)

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__
                return 0

        if not args:
            raise Usage("missing command argument")

        command = args[0]
        if command not in command_table:
            hits = []
            for c in command_table:
                if c.startswith(command):
                    hits.append(c)
            if not hits:
                raise Usage("unrecognized command", command)
            if len(hits) > 1:
                raise Usage("ambiguous command abbreviation %r (%s)",
                            command, "|".join(hits))
            command = hits[0]

        short_opts, long_opts, handler = command_table[command]

        try:
            opts, args = getopt.getopt(args[1:], short_opts, long_opts)
        except getopt.error, msg:
            raise Usage("%s option error: %s", command, msg)

        return handler(opts, args)

    except Usage, msg:
        print >>sys.stderr, msg
        print >>sys.stderr, "for help use --help"
        return 2

    except Error, msg:
        print >>sys.stderr, msg
        return 1

    else:
        return None

def checkout(opts, args):
    if not args:
        raise Usage("commit requires a URL argument")
    rooturl = args[0]
    if len(args) > 1:
        target = args[0]
        if len(args) > 2:
            raise Usage("commit requires at most one TARGETDIR argument")
    else:
        target = os.curdir
    fs = FSSync(rooturl=rooturl)
    fs.checkout(target)

def commit(opts, args):
    fs = FSSync()
    fs.multiple(args, fs.commit)

def update(opts, args):
    fs = FSSync()
    fs.multiple(args, fs.update)

def add(opts, args):
    fs = FSSync()
    for a in args:
        fs.add(a)

def remove(opts, args):
    fs = FSSync()
    for a in args:
        fs.remove(a)

diffflags = ["-b", "-B", "--brief", "-c", "-C", "--context=",
             "-i", "-u", "-U", "--unified"]
def diff(opts, args):
    diffopts = []
    mode = 1
    for o, a in opts:
        if o == '-1':
            mode = 1
        elif o == '-2':
            mode = 2
        elif o == '-3':
            mode = 3
        elif o in diffflags:
            if a:
                diffopts.append(o + " " + a)
            else:
                diffopts.append(o)
    diffopts = " ".join(diffopts)
    fs = FSSync()
    def calldiff(arg):
        fs.diff(arg, mode, diffopts)
    fs.multiple(args, calldiff)

command_table = {
    "checkout": ("", [], checkout),
    "co":       ("", [], checkout),
    "update":   ("", [], update),
    "commit":   ("", [], commit),
    "add":      ("", [], add),
    "remove":   ("", [], remove),
    "rm":       ("", [], remove),
    "r":        ("", [], remove),
    "diff":     ("bBcC:iuU:", ["brief", "context=", "unified="], diff),
    }

if __name__ == "__main__":
    sys.exit(main(sys.argv))
