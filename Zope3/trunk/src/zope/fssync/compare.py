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
"""Tools to compare parallel trees as written by toFS().

$Id: compare.py,v 1.1 2003/05/09 20:54:15 gvanrossum Exp $
"""

from __future__ import generators

import os
import filecmp

from os.path import exists, isfile, isdir, join, normcase

from zope.xmlpickle import loads

def checkUptodate(working, current):
    """Up-to-date check before committing changes.

    Given a working tree containing the user's changes and Original
    subtrees, and a current tree containing the current state of the
    database (for the same object tree), decide whether all the
    Original entries in the working tree match the entries in the
    current tree.  Return a list of error messages if something's
    wrong, [] if everything is up-to-date.
    """
    if not isdir(current):
        return []
    if not isdir(working):
        return ["missing working directory %r" % working]
    errors = []
    for (left, right, common, lentries, rentries, ldirs, lnondirs,
         rdirs, rnondirs) in treeComparisonWalker(working, current):
        if rentries:
            # Current has entries that working doesn't (the reverse
            # means things added to working, which is fine)
            for x in rentries:
                errors.append("missing working entry for %r" % join(left, x))
        for x in common:
            nx = normcase(x)
            if nx in rnondirs:
                # Compare files (directories are compared by the walk)
                lfile = join(left, "@@Zope", "Original", x)
                rfile = join(right, x)
                if not isfile(lfile):
                    errors.append("missing working original file %r" % lfile)
                elif not filecmp.cmp(lfile, rfile, shallow=False):
                    errors.append("files %r and %r differ" % (lfile, rfile))
            # Compare extra data (always)
            lextra = join(left, "@@Zope", "Extra", x)
            rextra = join(right, "@@Zope", "Extra", x)
            errors.extend(checkUptodate(lextra, rextra))
            # Compare annotations (always)
            lann = join(left, "@@Zope", "Annotations", x)
            rann = join(right, "@@Zope", "Annotations", x)
            errors.extend(checkUptodate(lann, rann))
    return errors

def treeComparisonWalker(left, right):
    """Generator that walks two parallel trees created by toFS().

    Each item yielded is a tuple of 9 items:

    left     -- left directory path
    right    -- right directory path
    common   -- dict mapping common entry names to (left, right) entry dicts
    lentries -- entry dicts unique to left
    rentries -- entry dicts unique to right
    ldirs    -- names of subdirectories of left
    lnondirs -- nondirectory names in left
    rdirs    -- names subdirectories of right
    rnondirs -- nondirectory names in right

    It's okay for the caller to modify the dicts to affect the rest of
    the walk.

    IOError exceptions may be raised.
    """
    # XXX There may be problems on a case-insensitive filesystem when
    # the Entries.xml file mentions two objects whose name only
    # differs in case.  Otherwise, case-insensitive filesystems are
    # handled correctly.
    queue = [(left, right)]
    while queue:
        left, right = queue.pop(0)
        lentries = loadEntries(left)
        rentries = loadEntries(right)
        common = {}
        for key in lentries.keys():
            if key in rentries:
                common[key] = lentries[key], rentries[key]
                del lentries[key], rentries[key]
        ldirs, lnondirs = classifyContents(left)
        rdirs, rnondirs = classifyContents(right)
        yield (left, right,
               common, lentries, rentries,
               ldirs, lnondirs, rdirs, rnondirs)
        commonkeys = common.keys()
        commonkeys.sort()
        for x in commonkeys:
            nx = normcase(x)
            if nx in ldirs and nx in rdirs:
                queue.append((ldirs[nx], rdirs[nx]))
        # XXX Need to push @@Zope/Annotations/ and @@Zope/Extra/ as well.

nczope = normcase("@@Zope")             # Constant used by classifyContents

def classifyContents(path):
    """Classify contents of a directory into directories and non-directories.

    Return a pair of dicts, the first containing directory names, the
    second containing names of non-directories.  Each dict maps the
    normcase'd version of the name to the path formed by concatenating
    the path with the original name.  '@@Zope' is excluded.
    """
    dirs = {}
    nondirs = {}
    for name in os.listdir(path):
        ncname = normcase(name)
        if ncname == nczope:
            continue
        full = join(path, name)
        if isdir(full):
            dirs[ncname] = full
        else:
            nondirs[ncname] = full
    return dirs, nondirs

def loadEntries(dir):
    """Return the Entries.xml file as a dict; default to {}."""
    filename = join(dir, "@@Zope", "Entries.xml")
    if exists(filename):
        f = open(filename)
        data = f.read()
        f.close()
        return loads(data)
    else:
        return {}
