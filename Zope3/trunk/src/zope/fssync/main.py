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
fssync [global_options] status [local_options] [TARGET ...]
fssync [global_options] add [local_options] TARGET ...
fssync [global_options] remove [local_options] TARGET ...

For now, the only option (local as well as global) is -h or --help;
there are no other options yet except for diff, which supports a small
subset of the options of GNU diff as local options.

``fssync -h'' prints the global help (this message)
``fssync command -h'' prints the local help for the command
"""
"""
$Id: main.py,v 1.14 2003/05/15 15:32:23 gvanrossum Exp $
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

from zope.fssync.fsutil import Error
from zope.fssync.fssync import FSSync

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
            opts, args = getopt.getopt(args[1:],
                                       "h"+short_opts,
                                       ["help"] + long_opts)
        except getopt.error, msg:
            raise Usage("%s option error: %s", command, msg)

        if ("-h", "") in opts or ("--help", "") in opts:
            print handler.__doc__ or "No help for %s" % handler.__name__
            return 0

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
    """fssync checkout URL [TARGETDIR]

    URL should be of the form ``http://user:password@host:port/path''.
    Only http and https are supported (and https only where Python has
    been built to support SSL).  This should identify a Zope 3 server;
    user:password should have management privileges; /path should be
    the traversal path to an existing object, not including views or
    skins.

    TARGETDIR should be a directory; if it doesn't exist, it will be
    created.  The object tree rooted at /path is copied to a
    subdirectory of TARGETDIR whose name is the last component of
    /path.  TARGETDIR defaults to the current directory.  A metadata
    directory named @@Zope is also created in TARGETDIR.
    """
    if not args:
        raise Usage("checkout requires a URL argument")
    rooturl = args[0]
    if len(args) > 1:
        target = args[1]
        if len(args) > 2:
            raise Usage("checkout requires at most one TARGETDIR argument")
    else:
        target = os.curdir
    fs = FSSync(rooturl=rooturl)
    fs.checkout(target)

def commit(opts, args):
    """fssync commit [TARGET ...]

    Commit the TARGET files or directories to the Zope 3 server
    identified by the checkout command.  TARGET defaults to the
    current directory.  Each TARGET is committed separately.  Each
    TARGET should be up-to-date with respect to the state of the Zope
    3 server; if not, a detailed error message will be printed, and
    you should use the update command to bring your working directory
    in sync with the server.
    """
    fs = FSSync()
    fs.multiple(args, fs.commit)

def update(opts, args):
    """fssync update [TARGET ...]

    Bring the TARGET files or directories in sync with the
    corresponding objects on the Zope 3 server identified by the
    checkout command.  TARGET defaults to the current directory.  Each
    TARGET is updated independently.  This command will merge your
    changes with changes made on the server; merge conflicts will be
    indicated by diff3 markings in the file and noted by a 'C' in the
    update output.
    """
    fs = FSSync()
    fs.multiple(args, fs.update)

def add(opts, args):
    """fssync add TARGET ...

    Add the TARGET files or directories to the set of registered
    objects.  Each TARGET must exist.  The next commit will add them
    to the Zope 3 server.
    """
    fs = FSSync()
    for a in args:
        fs.add(a)

def remove(opts, args):
    """fssync remove TARGET ...

    Remove the TARGET files or directories from the set of registered
    objects.  No TARGET must exist.  The next commit will remove them
    from the Zope 3 server.
    """
    fs = FSSync()
    for a in args:
        fs.remove(a)

diffflags = ["-b", "-B", "--brief", "-c", "-C", "--context",
             "-i", "-u", "-U", "--unified"]
def diff(opts, args):
    """fssync diff [diff_options] [TARGET ...]

    Write a diff listing for the TARGET files or directories to
    standard output.  This shows the differences between the working
    version and the version seen on the server by the last update.
    Nothing is printed for files that are unchanged from that version.
    For directories, a recursive diff is used.

    Various GNU diff options can be used, in particular -c, -C NUMBER,
    -u, -U NUMBER, -b, -B, --brief, and -i.
    """
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

def status(opts, args):
    """fssync status [TARGET ...]

    Print brief (local) status for each target, without changing any files.
    """
    fs = FSSync()
    fs.multiple(args, fs.status)

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
    "status":   ("", [], status),
    }

if __name__ == "__main__":
    sys.exit(main(sys.argv))
