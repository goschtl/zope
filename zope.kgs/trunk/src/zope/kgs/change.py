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
import sys
import xmlrpclib
import zope.kgs.kgs

SERVER_URL = "http://cheeseshop.python.org/pypi"

def extractChanges(text, firstVersion, lastVersion):
    return text[text.find(lastVersion):text.find(firstVersion)]

def generateChanges(currentPath, origPath):
    kgs = zope.kgs.kgs.KGS(currentPath)
    server = xmlrpclib.Server(SERVER_URL)

    origVersions = {}
    if origPath:
        origKgs = zope.kgs.kgs.KGS(origPath)
        for package in origKgs.packages:
            origVersions[package.name] = package.versions[-1]

    changes = []

    for package in kgs.packages:
        data = server.release_data(package.name, package.versions[-1])
        firstVersion = origVersions.get(package.name, package.versions[0])
        lastVersion = package.versions[-1]
        changes.append(
            (package.name, firstVersion, lastVersion,
             extractChanges(data['description'], firstVersion, lastVersion))
            )

    return changes

def printChanges(changes):
    for name, firstVersion, lastVersion, changes in changes:
        print '%s (%s - %s)' %(name, firstVersion, lastVersion)
        print '='*(len(name+firstVersion+lastVersion)+6)
        print
        print changes
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
