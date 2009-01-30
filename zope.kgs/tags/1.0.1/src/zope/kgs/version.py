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
"""Generate a ``latest-versions.cfg`` file from the controlled list of
packages.

Usage: %s package-cfg-path [output-cfg-path]

* ``package-cfg-path``

  This is the path to the controlled packages configuration file.

* ``output-cfg-path``

  The path of the file under which the generated buildout configuration file
  is stored. By default it is placed in the package configuration file's
  directory under the name 'latest-versions.cfg'.

"""
import os
import sys

from zope.kgs import buildout, kgs

def generateVersions(packageConfigPath, outputPath):
    """Generate a ``buildout.cfg`` from the list of controlled packages."""
    # Load all package information from the controlled pacakge config file.
    packages = kgs.KGS(packageConfigPath).packages

    # Write a new versions.cfg file
    open(outputPath, 'w').write(
        '[versions]\n' +
        buildout.getVersionsListing(packages))


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print __doc__ %sys.argv[0]
        sys.exit(1)

    packageConfigPath = os.path.abspath(args[0])

    outputPath = os.path.join(
        os.path.dirname(packageConfigPath), 'latest-versions.cfg')
    if len(args) == 2:
        outputPath = args[1]

    generateVersions(packageConfigPath, outputPath)
