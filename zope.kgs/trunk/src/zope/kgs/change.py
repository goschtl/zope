##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""For each package in the KGS that changed since a previous release, produce
a list of changes. If the original KGS is not specified, all entries in the
KGS are assumed to be new.

Usage: %s current-package-cfg-path [orig-package-cfg-path]

* ``orig-package-cfg-path``

  This is the path to the original controlled packages configuration file.

* ``current-package-cfg-path``

  This is the path to the current controlled packages configuration file.

"""
import os
import pickle
import re
import sys
import xmlrpclib
import pkg_resources
import zope.kgs.kgs

SERVER_URL = "http://cheeseshop.python.org/pypi"

def loadCache(fn):
    if os.path.exists(fn):
        return pickle.load(open(fn))
    return {}

def saveCache(fn, cache):
    pickle.dump(cache, open(fn, 'w'))

# version_line finds a version number and an optional date
version_line = re.compile(
    r"(version\s*|)([0-9.][0-9a-zA-Z.]*)(\s*[(]([0-9a-z?-]+)[)])?",
    re.IGNORECASE)

# decoration_line matches lines to ignore
decoration_line = re.compile(r"---|===")

def parseReleases(lines):
    """Parse the list of releases from a CHANGES.txt file.

    Yields (version, release_date, [line]) for each release listed in the
    change log.
    """
    if isinstance(lines, basestring):
        lines = lines.split('\n')

    version = None
    release_date = None
    changes = None

    for line in lines:
        line = line.rstrip()
        mo = version_line.match(line)
        if mo is not None:
            if changes is not None:
                yield version, release_date, changes
            changes = []
            version = mo.group(2)
            release_date = mo.group(4)
        elif changes is not None and decoration_line.match(line) is None:
            changes.append(line)

    # include the last list of changes
    if version is not None and changes is not None:
        yield version, release_date, changes

def extractChanges(text, firstVersion, lastVersion):
    """Parse the changes out of a CHANGES.txt in the given range.

    For each release, yields (version, release_date, change text).
    """
    first = pkg_resources.parse_version(firstVersion)
    last = pkg_resources.parse_version(lastVersion)
    for version, release_date, changes in parseReleases(text):
        try:
            v = pkg_resources.parse_version(version)
        except AttributeError:
            import pdb; pdb.set_trace()
            raise
        if first <= v <= last:
            yield version, release_date, '\n'.join(changes)


def generateChanges(currentPath, origPath):
    kgs = zope.kgs.kgs.KGS(currentPath)
    server = xmlrpclib.Server(SERVER_URL)

    origVersions = {}
    if origPath:
        origKgs = zope.kgs.kgs.KGS(origPath)
        for package in origKgs.packages:
            origVersions[package.name] = package.versions[-1]

    changes = []

    cache = loadCache('descriptions.dat')

    for package in kgs.packages:
        key = package.name, package.versions[-1]
        print key
        if key in cache:
            description = cache[key]
        else:
            data = server.release_data(package.name, package.versions[-1])
            cache[key] = description = data['description']
            saveCache('descriptions.dat', cache)

        firstVersion = origVersions.get(package.name, package.versions[0])
        lastVersion = package.versions[-1]
        versions = list(
            extractChanges(description, firstVersion, lastVersion))
        changes.append((package.name, versions))

    return changes


def printChanges(changes):
    for name, versions in changes:
        print '=' * len(name)
        print name
        print '=' * len(name)
        print
        for version, release_date, text in versions:
            s = '%s (%s)' % (version, release_date)
            print s
            print '-' * len(s)
            print
            print text.strip()
            print
        print


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1 or args[0] in ('-h', '--help'):
        print __file__.__doc__ % sys.argv[0]
        sys.exit(1)

    currentPackageConfigPath = os.path.abspath(args[0])
    origPackageConfigPath = None
    if len(args) > 1:
        origPackageConfigPath = os.path.abspath(args[1])

    changes = generateChanges(currentPackageConfigPath, origPackageConfigPath)
    printChanges(changes)
