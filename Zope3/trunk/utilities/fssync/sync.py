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

import sys, string, getopt, os, commands

# Hack to fix the module search path
try:
    import zope.app
    # All is well
except ImportError:
    # Fix the path, assuming this script is <root>/utilities/fssync/sync.py
    # and the zope module is <root>/src/zope/.
    _script = sys.argv[0]
    _scriptdir = os.path.abspath(os.path.dirname(_script))
    _rootdir = os.path.dirname(os.path.dirname(_scriptdir))
    _srcdir = os.path.join(_rootdir, "src")
    sys.path.append(_srcdir)

from diff import getdiff
from common import checkFSPath, setPrint
from checkout import checkout
from commit import commit
from update import update
from usage import USAGE
from add import add, addTypes

def main(argv):
    short_options = ':f:o:d:s:1:2:3:t:'
    long_options = ['fspath='
                   , 'objpath='
                   , 'dbpath='
                   , 'siteconfpath=']

    operations = ['commit'
                 , 'checkout'
                 , 'update'
                 , 'diff'
                 , 'fcommit'
                 , 'add'
                 , 'addtypes']

    err = ""

    usage = USAGE % argv[0]

    try:
        optlist, args = getopt.getopt(sys.argv[1:]
                                      , short_options
                                      , long_options)

        env=os.environ

        objpath = ''
        operation = ''
        targetfile = ''
        diffoption = '-1'
        newobjectname = ''
        newobjecttype = ''

        if env.has_key('SYNCROOT'): fspath = env['SYNCROOT']
        else: fspath = '.'
        if env.has_key('ZODBPATH'): dbpath = env['ZODBPATH']
        else: dbpath = '../../../Data.fs'
        if env.has_key('SITECONFPATH'): siteconfpath = env['SITECONFPATH']
        else: siteconfpath = '../../../site.zcml'

        if len(optlist) > 0  or len(args) > 0:
            for opt in optlist:
                if (opt[0] == '-f') or (opt[0] == '--fspath'):
                    fspath = opt[1]
                elif (opt[0] == '-o') or (opt[0] == '--objpath'):
                    objpath = opt[1]
                elif (opt[0] == '-d') or (opt[0] == '--dbpath'):
                    dbpath = opt[1]
                elif (opt[0] == '-s') or (opt[0] == '--siteconfpath'):
                    siteconfpath = opt[1]
                elif (opt[0] == '-1' or opt[0] == '-2' or opt[0] == '-3'):
                    diffoption = opt[0]
                    targetfile = opt[1]
                elif opt[0] == '-t':
                    newobjecttype = opt[1]

            newobjectname = args[1:]

            if len(args) <1:
                err = "No operation has been specified"
                raise err
            elif args[0] != 'add' and len(args) >1:
                err = "CommandlineError"
                raise err
            elif args[0] not in operations:
                err = "Invalid operation---"+str(args[0])
                raise err
            else:
                operation = args[0]

            fspath, dbpath, siteconfpath = (os.path.abspath(fspath)
                                            , os.path.abspath(dbpath)
                                            , os.path.abspath(siteconfpath))
            path=[fspath, dbpath, siteconfpath]
            err=checkFSPath(path)
            if err is not None:
                raise err

        else:
            if len(args)>1:
                if args[1]=='diff':
                    targetfile = args[0]
                    operation = args[1]
                else:
                    setPrint(usage)
                    sys.exit(1)
            else:
                setPrint(usage)
                sys.exit(1)

        #Calls the specified operation
        err = operate(operation
                      , fspath
                      , dbpath
                      , siteconfpath
                      , objpath
                      , targetfile
                      , diffoption
                      , newobjecttype
                      , newobjectname)
        if err is not None:
            raise err

    except err:
        setPrint(err)
        sys.exit(1)




def operate(operation
            , fspath
            , dbpath
            , siteconfpath
            , objpath
            , targetfile
            , diffoption
            , newobjecttype
            , newobjectname):
    """Operates based on the operations passed
    """
    err=""
    if operation == 'checkout':
        err = checkout(fspath
                       , dbpath
                       , siteconfpath
                       , objpath)
    elif operation == 'commit':
        err = commit(fspath
                     , dbpath
                     , siteconfpath)
    elif operation == 'update':
        err = update(fspath
                     , dbpath
                     , siteconfpath)
    elif operation == 'diff':
        err = getdiff(targetfile
                      , objpath
                      , dbpath
                      , siteconfpath
                      , diffoption)
    elif operation == 'fcommit':
        err = commit(fspath
                     , dbpath
                     , siteconfpath
                     , 'F')
    elif operation == 'add':
        err = add(fspath
                  , dbpath
                  , siteconfpath
                  , newobjecttype
                  , newobjectname)
    elif operation == 'addtypes':
        err = addTypes(dbpath
                       , siteconfpath)

    return err


# If called from the command line
if __name__=='__main__': main(sys.argv)
