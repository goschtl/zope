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
"""New fssync utility.

Connects to the database using HTTP (using the toFS.zip view for
checkout and update and the fromFS.form view for commit).

An attempt is made to make the behavior similar to that of cvs.

Command line syntax summary:

fssync checkout URL TARGETDIR
fssync update [FILE_OR_DIR ...]
fssync status [FILE_OR_DIR ...]
fssync commit [FILE_OR_DIR ...]
fssync diff [FILE_OR_DIR ...]

$Id: main.py,v 1.1 2003/05/09 20:54:15 gvanrossum Exp $
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
    import zope.xmlpickle
    # All is well
except ImportError:
    # Fix the path to include <root>/src
    srcdir = join(rootdir, "src")
    sys.path.append(srcdir)

from zope.xmlpickle import loads, dumps

from zope.fssync.fssync import Error, FSSync

class Usage(Error):
    """Subclass for usage error (command-line syntax).

    This should set an exit status of 2 rather than 1.
    """

def main(argv=None):
    try:
        if argv is None:
            argv = sys.argv
        # XXX getopt
        args = argv[1:]
        command = args[0]
        # XXX more getopt
        args = args[1:]
        if command in ("checkout", "co"):
            url, fspath = args
            checkout(url, fspath)
        elif command in ("update", "up"):
            args = args or [os.curdir]
            for fspath in args:
                print "update(%r)" % fspath
                update(fspath)
        elif command in ("commit", "com"):
            args = args or [os.curdir]
            [fspath] = args
            commit(fspath)
        else:
            raise Usage("command %r not recognized" % command)
    except Usage, msg:
        print msg
        print "for help use --help"
        return 2
    except Error, msg:
        print msg
        return 1
    else:
        return None

def checkout(url, fspath, writeOriginals=True):
    fs = FSSync(fspath)
    fs.setrooturl(url)
    fs.checkout()

def commit(fspath):
    fs = FSSync(fspath)
    fs.commit()

def update(fspath):
    fs = FSSync(fspath)
    fs.update()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
