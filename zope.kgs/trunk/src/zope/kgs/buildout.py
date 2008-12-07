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
"""Generate a ``buildout.cfg`` file from the controlled list of packages.

Usage: generate-buildout package-cfg-path [output-cfg-path]

* ``package-cfg-path``

  This is the path to the controlled packages configuration file.

* ``output-cfg-path``

  The path of the file under which the generated buildout configuration file
  is stored. By default it is placed in the package configuration file's
  directory under the name 'test-buildout.cfg'.

"""
import os

from zope.kgs import kgs

def getVersionsListing(packages):
    """Create a version listing string."""
    return '\n'.join(
        [package.name + ' = ' + package.versions[-1]
         for package in packages])


def generateBuildout(packageConfigPath, outputPath):
    """Generate a ``buildout.cfg`` from the list of controlled packages."""
    # Load all package information from the controlled pacakge config file.
    packages = kgs.KGS(packageConfigPath).packages

    # Create the data dictionary
    data = {
        'tested-packages': '\n    '.join(
            [package.name for package in packages if package.tested]),
        'versions': getVersionsListing(packages)
        }

    # Write a new buildout.cfg file
    templatePath = os.path.join(os.path.dirname(__file__), 'buildout.cfg.in')
    open(outputPath, 'w').write(open(templatePath, 'r').read() %data)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print __file__.__doc__
        sys.exit(1)

    packageConfigPath = os.path.abspath(args[0])

    outputPath = os.path.join(
        os.path.dirname(packageConfigPath), 'test-buildout.cfg')
    if len(args) == 2:
        outputPath = args[1]

    generateBuildout(packageConfigPath, outputPath)
