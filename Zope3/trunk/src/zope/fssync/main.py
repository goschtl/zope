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

%(program)s [global_options] checkout [local_options] URL [TARGETDIR]
%(program)s [global_options] update [local_options] [TARGET ...]
%(program)s [global_options] commit [local_options] [TARGET ...]
%(program)s [global_options] diff [local_options] [TARGET ...]
%(program)s [global_options] status [local_options] [TARGET ...]
%(program)s [global_options] add [local_options] TARGET ...
%(program)s [global_options] remove [local_options] TARGET ...
%(program)s [global_options] checkin [local_options] URL [TARGETDIR]

``%(program)s -h'' prints the global help (this message)
``%(program)s command -h'' prints the local help for the command
"""
"""
$Id: main.py,v 1.24 2003/08/07 20:38:02 fdrake Exp $
"""

import os
import sys
import getopt

from os.path import dirname, join, realpath

# Find the zope root directory.
# XXX This assumes this script is <root>/src/zope/fssync/main.py
scriptfile = realpath(sys.argv[0])
scriptdir = dirname(scriptfile)
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

        progname = os.path.basename(argv[0])

        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help"])
        except getopt.error, msg:
            raise Usage("global option error: %s", msg)

        for o, a in opts:
            if o in ("-h", "--help"):
                print __doc__ % {"program": progname}
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
            message = handler.__doc__ or "No help for %s" % handler.__name__
            print message % {"program": progname}
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
    """%(program)s checkout URL [TARGETDIR]

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
    """%(program)s commit [-m message] [-r] [TARGET ...]

    Commit the TARGET files or directories to the Zope 3 server
    identified by the checkout command.  TARGET defaults to the
    current directory.  Each TARGET is committed separately.  Each
    TARGET should be up-to-date with respect to the state of the Zope
    3 server; if not, a detailed error message will be printed, and
    you should use the update command to bring your working directory
    in sync with the server.

    The -m option specifies a message to label the transaction.
    The default message is 'fssync_commit'.
    """
    message, opts = extract_message(opts, "commit")
    raise_on_conflicts = False
    for o, a in opts:
        if o in ("-r", "--raise-on-conflicts"):
            raise_on_conflicts = True
    fs = FSSync()
    fs.multiple(args, fs.commit, message, raise_on_conflicts)

def update(opts, args):
    """%(program)s update [TARGET ...]

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
    """%(program)s add [-t TYPE] [-f FACTORY] TARGET ...

    Add the TARGET files or directories to the set of registered
    objects.  Each TARGET must exist.  The next commit will add them
    to the Zope 3 server.

    The options -t and -f can be used to set the type and factory of
    the newly created object; these should be dotted names of Python
    objects.  Usually only the factory needs to be specified.

    If no factory is specified, the type will be guessed when the
    object is inserted into the Zope 3 server based on the filename
    extension and the contents of the data.  For example, some common
    image types are recognized by their contents, and the extensions
    .pt and .dtml are used to create page templates and DTML
    templates, respectively.
    """
    type = None
    factory = None
    for o, a in opts:
        if o in ("-t", "--type"):
            type = a
        elif o in ("-f", "--factory"):
            factory = a
    if not args:
        raise Usage("add requires at least one TARGET argument")
    fs = FSSync()
    for a in args:
        fs.add(a, type, factory)

def remove(opts, args):
    """%(program)s remove TARGET ...

    Remove the TARGET files or directories from the set of registered
    objects.  No TARGET must exist.  The next commit will remove them
    from the Zope 3 server.
    """
    if not args:
        raise Usage("remove requires at least one TARGET argument")
    fs = FSSync()
    for a in args:
        fs.remove(a)

diffflags = ["-b", "-B", "--brief", "-c", "-C", "--context",
             "-i", "-u", "-U", "--unified"]
def diff(opts, args):
    """%(program)s diff [diff_options] [TARGET ...]

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
    need_original = True
    for o, a in opts:
        if o == '-1':
            mode = 1
        elif o == '-2':
            mode = 2
        elif o == '-3':
            mode = 3
        elif o == '-N':
            need_original = False
        elif o in diffflags:
            if a:
                diffopts.append(o + " " + a)
            else:
                diffopts.append(o)
    diffopts = " ".join(diffopts)
    fs = FSSync()
    fs.multiple(args, fs.diff, mode, diffopts, need_original)

def status(opts, args):
    """%(program)s status [TARGET ...]

    Print brief (local) status for each target, without changing any files.
    """
    fs = FSSync()
    fs.multiple(args, fs.status)

def checkin(opts, args):
    """%(program)s checkin [-m message] URL [TARGETDIR]

    URL should be of the form ``http://user:password@host:port/path''.
    Only http and https are supported (and https only where Python has
    been built to support SSL).  This should identify a Zope 3 server;
    user:password should have management privileges; /path should be
    the traversal path to a non-existing object, not including views
    or skins.

    TARGETDIR should be a directory; it defaults to the current
    directory.  The object tree rooted at TARGETDIR is copied to
    /path.  subdirectory of TARGETDIR whose name is the last component
    of /path.
    """
    message, opts = extract_message(opts, "checkin")
    if not args:
        raise Usage("checkin requires a URL argument")
    rooturl = args[0]
    if len(args) > 1:
        target = args[1]
        if len(args) > 2:
            raise Usage("checkin requires at most one TARGETDIR argument")
    else:
        target = os.curdir
    fs = FSSync(rooturl=rooturl)
    fs.checkin(target, message)

def extract_message(opts, cmd):
    L = []
    message = None
    msgfile = None
    for o, a in opts:
        if o in ("-m", "--message"):
            if message:
                raise Usage(cmd + " accepts at most one -m/--message option")
            message = a
        elif o in ("-F", "--file"):
            if msgfile:
                raise Usage(cmd + " accepts at most one -F/--file option")
            msgfile = a
        else:
            L.append((o, a))
    if not message:
        if msgfile:
            message = open(msgfile).read()
        else:
            message = "fssync_" + cmd
    elif msgfile:
        raise Usage(cmd + " requires at most one of -F/--file or -m/--message")
    return message, L

command_table = {
    "checkout": ("", [], checkout),
    "co":       ("", [], checkout),
    "update":   ("", [], update),
    "commit":   ("F:m:r", ["file=", "message=", "raise-on-conflicts"], commit),
    "add":      ("f:t:", ["factory=", "type="], add),
    "remove":   ("", [], remove),
    "rm":       ("", [], remove),
    "r":        ("", [], remove),
    "diff":     ("bBcC:iNuU:", ["brief", "context=", "unified="], diff),
    "status":   ("", [], status),
    "checkin":  ("F:m:", ["file=", "message="], checkin),
    "ci":       ("F:m:", ["file=", "message="], checkin),
    }

if __name__ == "__main__":
    sys.exit(main(sys.argv))
