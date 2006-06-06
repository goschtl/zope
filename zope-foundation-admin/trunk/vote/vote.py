#!/usr/local/bin/python2.4
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
"""Dirt-simple voting app

There is a directory: /foundation/votes

This directory is writable only by zf committer members.
(Enforced using a group.)

There is a subdirectory for each question.  When a question is
open for voting, the directory is writable.

The vote command is invoked via ssh:

  ssh svn.zope.com vote issueid args

an issue has an associated "schema".  This is a
Python file containing two functions, validate, and count.
The validate method validates a sequence of arguments.
The count methods prints the current results.

When someone votes, their input is validates and, if valid:

  - Their vote is written to a file with the same name as their
    login id

  - The results of all votes (the output of count) is printed.

If the vote command is invoked with an issue id but no arguments,
then the current results are printed.

$Id$
"""

import os, pwd, re, sys

votes = os.path.dirname(os.path.realpath(__file__))
print votes

valid_issueid = re.compile('\w+$').match

def error(mess):
    print mess
    sys.exit(1)

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    if not args:
        error("Usage: vote issueid [arguments]")
    issueid, args = args[0], args[1:]
    if not valid_issueid(issueid):
        error("Invalid issue id")
    
    issuefolder = os.path.join(votes, issueid)
    if not os.path.isdir(issuefolder):
        error("Invalid issue id")

    if not os.access(issuefolder, os.W_OK):
        error("Voting is closed")

    issueschema = os.path.join(votes, issueid+'.py')
    if not os.path.exists(issueschema):
        error("Invalid issue id")

    execfile(issueschema, globals())

    uname = pwd.getpwuid(os.geteuid())[0]
    if args:
        validate(issuefolder, args)
        open(os.path.join(issuefolder, uname), 'w').write('\n'.join(args))

    if os.access(issuefolder, os.R_OK):
        count(issuefolder, uname)
    else:
        print 'Vote results are not available'
    
if __name__ == '__main__':
    main()
