#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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

"""Command line processor for Filesystem synchronization utility.

The command line is of the form:

    program [options] command [arguments]
"""

import sys, getopt, os, commands

# Find the zope root directory.
# XXX This assumes this script is <root>/utilities/fssync/sync.py
scriptfile = sys.argv[0]
scriptdir = os.path.realpath(os.path.dirname(scriptfile))
rootdir = os.path.dirname(os.path.dirname(scriptdir))

# Hack to fix the module search path
try:
    import zope.app
    # All is well
except ImportError:
    # Fix the path to include <root>/src
    srcdir = os.path.join(rootdir, "src")
    sys.path.append(srcdir)

from usage import USAGE
from diff import getdiff
from checkout import checkout
from commit import commit
from update import update
from add import add, addTypes

def main(argv):
    """Main function.  Pass sys.argv.  Returns exit code for sys.exit()."""

    short_options = 'f:o:d:s:1:2:3:t:h'
    long_options = ['fspath=', 'objpath=', 'dbpath=', 'siteconfpath=', "help"]

    try:
        opts, args = getopt.getopt(argv[1:], short_options, long_options)
    except getopt.error, msg:
        return usage(msg)

    if not opts and not args:
        return usage()

    if not args:
        return usage("no command specified")

    known_operations = ['checkout', 'update', 'add', 'addtypes', 'diff',
                        'commit', 'fcommit']

    operation = args[0]
    if operation not in known_operations:
        return usage("command %r is not a known operation" % operation)

    newobjectname = args[1:]
    if newobjectname and operation != 'add':
        return usage("only command 'add' takes arguments")

    objpath = ''
    targetfile = ''
    diffoption = '-1'
    newobjecttype = ''

    fspath = os.curdir
    dbpath = os.path.join(rootdir, 'Data.fs')
    siteconfpath = os.path.join(rootdir, 'site.zcml')

    env = os.environ
    if env.has_key('SYNCROOT'):
        fspath = env['SYNCROOT']
    if env.has_key('ZODBPATH'):
        dbpath = env['ZODBPATH']
    if env.has_key('SITECONFPATH'):
        siteconfpath = env['SITECONFPATH']

    for o, a in opts:
        if o in ('-h', '--help'):
            print USAGE % argv[0]
            return 0
        elif o in ('-f', '--fspath'):
            fspath = a
        elif o in ('-o', '--objpath'):
            objpath = a
        elif o in ('-d', '--dbpath'):
            dbpath = a
        elif o in ('-s', '--siteconfpath'):
            siteconfpath = a
        elif o in ('-1', '-2', '-3'):
            diffoption = o
            targetfile = a
        elif o == '-t':
            newobjecttype = a

    fspath = os.path.realpath(fspath)
    if patherror("fspath(.)", fspath):
        return 1
    dbpath = os.path.realpath(dbpath)
    if patherror("dbpath(Data.fs)", dbpath):
        return 1
    siteconfpath = os.path.realpath(siteconfpath)
    if patherror("siteconfpath(site.zcml)", siteconfpath):
        return 1

    if operation == 'checkout':
        err = checkout(fspath, dbpath, siteconfpath, objpath)
    elif operation == 'update':
        err = update(fspath, dbpath, siteconfpath)
    elif operation == 'add':
        err = add(fspath, dbpath, siteconfpath, newobjecttype, newobjectname)
    elif operation == 'addtypes':
        err = addTypes(dbpath, siteconfpath)
    elif operation == 'diff':
        err = getdiff(targetfile, objpath, dbpath, siteconfpath, diffoption)
    elif operation == 'commit':
        err = commit(fspath, dbpath, siteconfpath)
    elif operation == 'fcommit':
        err = commit(fspath, dbpath, siteconfpath, 'F')
    else:
        # Can't happen
        assert 0, "Unsupported operation name: %r" % operation

    if err:
        print err
        return 1
    else:
        return 0

def usage(msg=None):
    """Print short usage message and return usage exit code (2)."""
    if msg:
        print msg
    print "for help use --help"
    return 2

def patherror(what, path):
    """Check for existence of a path, print nice message if not."""
    if not os.path.exists(path):
        print "%s: path %r doesn't exist" % (what, path)
        return True
    else:
        return False

if __name__=='__main__':
    sys.exit(main(sys.argv))
