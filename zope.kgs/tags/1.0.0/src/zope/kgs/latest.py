##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""For each package in the KGS, find all versions later than the last one
listed in the KGS for that package.

Usage: %s [-m] package-cfg-path [packagename ...]

* -m

  Only list the versions that have the same major revision as the KGS version.

* ``package-cfg-path``

  This is the path to the controlled packages configuration file.

* ``packagename``

  If you're interested in only some of the KGS packages, you can limit the
  output to those by listing their names on the command line.

"""
import lxml.etree
import os
import pkg_resources
import re
import urllib
import urllib2
import zope.kgs.kgs

SIMPLE_BASE_URL = "http://cheeseshop.python.org/simple/"
VERSION_REGEX = '%s-(.*)(?:\.tar\.gz|\.zip)'

def getAllVersions(packageName):
    # Download the links URL, since the XML-RPC API does not provide the
    # versions of hidden releases. :-(
    packageName = urllib.quote(packageName)
    page = urllib2.urlopen(SIMPLE_BASE_URL + packageName + '/').read()
    # Parse the page to find all links that could possibly contain versoin
    # information.
    tree = lxml.etree.fromstring(page)
    # Extract the versions from the links.
    regex = re.compile(VERSION_REGEX %packageName)
    versions = []
    for url in tree.xpath('//a/@href'):
        res = regex.findall(url)
        if res and res[0] and res[0] not in versions:
            versions.append(res[0])
    return versions


def generateList(packageConfigPath, minorOnly, packages=()):
    kgs = zope.kgs.kgs.KGS(packageConfigPath)

    for package in kgs.packages:
        if packages and package.name not in packages:
            continue

        kgsVersion = pkg_resources.parse_version(package.versions[-1])
        serverVersions = getAllVersions(package.name)

        newVersions = []
        for version in serverVersions:
            parsedVersion = pkg_resources.parse_version(version)
            if minorOnly:
                if parsedVersion[:2] != kgsVersion[:2]:
                    continue
            if parsedVersion > kgsVersion:
                newVersions.append(version)

        newVersions.sort()
        if newVersions:
            print package.name + ': ' + ', '.join(newVersions)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1 or args[0] in ('-h', '--help'):
        print __file__.__doc__ % sys.argv[0]
        sys.exit(1)

    minorOnly = False
    if args[0] == '-m':
        minorOnly = True
        args = args[1:]

    packageConfigPath = os.path.abspath(args[0])

    generateList(packageConfigPath, minorOnly, args[1:])
