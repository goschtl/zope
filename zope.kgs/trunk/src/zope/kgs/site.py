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
"""Generates a full KGS site with all bells and whistles.

Usage: %s site-dir

* ``site-dir``

  The path to the directory where a ``controlled-packages.cfg`` file is
  located to generate the site. The generated site is in that directory as
  well.
"""
import os
import shutil
import sys
import time
from zope.kgs import version, buildout, ppix, link, intro, kgs

TIMESTAMP_FILENAME = 'cf-timestamp'

def generateSite(siteDir):
    kgsPath = os.path.join(siteDir, 'controlled-packages.cfg')
    ver = kgs.KGS(kgsPath).version

    timestampPath = os.path.join(siteDir, TIMESTAMP_FILENAME)

    # If there have been no changes in the file since the last generation,
    # simple do not do anything.
    if os.path.exists(timestampPath):
        last_update = float(open(timestampPath, 'r').read())
        last_modified = os.stat(kgsPath)[-2]
        if last_update > last_modified:
            return

    # Copy the KGS config file to a versioned version
    shutil.copy(
        kgsPath, os.path.join(siteDir, 'controlled-packages-%s.cfg' %ver))

    # Create the buildout config file and version it
    buildoutPath = os.path.join(siteDir, 'buildout.cfg')
    buildout.generateBuildout(kgsPath, buildoutPath)
    shutil.copy(buildoutPath, os.path.join(siteDir, 'buildout-%s.cfg' %ver))

    # Create a versions config file and version it
    versionsPath = os.path.join(siteDir, 'versions.cfg')
    version.generateVersions(kgsPath, versionsPath)
    shutil.copy(versionsPath, os.path.join(siteDir, 'versions-%s.cfg' %ver))

    # Create a links config file and version it
    linksPath = os.path.join(siteDir, 'links.cfg')
    link.generateLinks(kgsPath, linksPath)
    shutil.copy(linksPath, os.path.join(siteDir, 'links-%s.cfg' %ver))

    # Update the full index (which is asummed to live in the site directory)
    ppix.generatePackagePages(kgsPath, siteDir)

    # Update the minimal index
    midxDir = os.path.join(siteDir, 'minimal')
    if not os.path.exists(midxDir):
        os.mkdir(midxDir)
    ppix.generatePackagePages(kgsPath, midxDir)
    ppix.generateIndexPage(kgsPath, midxDir)

    # Update the intro page
    introPath = os.path.join(siteDir, 'intro.html')
    intro.main((introPath,))

    # Save the last generation date-time.
    open(timestampPath, 'w').write(str(time.time()))


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print __file__.__doc__ % sys.argv[0]
        sys.exit(1)

    siteDir = os.path.abspath(args[0])

    generateSite(siteDir)
