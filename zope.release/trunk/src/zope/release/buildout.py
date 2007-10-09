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

Usage: generate-buildout package-cfg-path index-url [output-cfg-path]

* ``package-cfg-path``

  This is the path to the controlled packages configuration file.

* ``index-url``

  The URL of the index to use. This is usually the index of the controlled
  pacakges.

* ``output-cfg-path``

  The path of the file under which the generated buildout configuration file
  is stored. By default it is placed in the package configuration file's
  directory under the name 'test-buildout.cfg'.

"""
import ConfigParser
import os

def getPackagesInfo(packageConfigPath):
    """Read all information from the controlled package configuration."""
    config = ConfigParser.RawConfigParser()
    config.read(packageConfigPath)
    packages = []
    sections = config.sections()
    sections.sort()
    for section in sections:
        packages.append((
            section,
            config.get(section, 'versions').split(),
            config.getboolean(section, 'tested')
            ))
    return packages


def getVersionsListing(packages):
    """Create a version listing string."""
    return '\n'.join(
        [name + ' = ' + version[-1]
         for (name, version, tested) in packages])


def generateBuildout(packageConfigPath, indexUrl, outputPath):
    """Generate a ``buildout.cfg`` from the list of controlled packages."""
    # Load all package information from the controlled pacakge config file.
    packages = getPackagesInfo(packageConfigPath)

    # Create the data dictionary
    data = {
        'index-url': indexUrl,
        'tested-packages': '\n    '.join(
            [p for (p, v, t) in packages if t]),
        'versions': getVersionsListing(packages)
        }

    # Write a new buildout.cfg file
    templatePath = os.path.join(os.path.dirname(__file__), 'buildout.cfg.in')
    open(outputPath, 'w').write(open(templatePath, 'r').read() %data)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 2:
        print __file__.__doc__
        sys.exit(1)

    packageConfigPath = os.path.abspath(args[0])
    indexUrl = args[1]

    outputPath = os.path.join(
        os.path.dirname(packageConfigPath), 'test-buildout.cfg')
    if len(args) == 3:
        outputPath = args[2]

    generateBuildout(packageConfigPath, indexUrl, outputPath)
