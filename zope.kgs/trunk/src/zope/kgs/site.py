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
import logging
import optparse
import os
import shutil
import sys
import time
from zope.kgs import version, buildout, ppix, link, intro, kgs

TIMESTAMP_FILENAME = 'cf-timestamp'
RESOURCES_PATH = os.path.join(os.path.dirname(__file__), 'templates','resources')

def generateSite(siteDir):
    kgsPath = os.path.join(siteDir, 'controlled-packages.cfg')
    ver = kgs.KGS(kgsPath).version
    logging.info("Building site for version %s using config: %s" % (ver, kgsPath))

    timestampPath = os.path.join(siteDir, TIMESTAMP_FILENAME)

    # If there have been no changes in the file since the last generation,
    # simple do not do anything.
    if os.path.exists(timestampPath):
        last_update = float(open(timestampPath, 'r').read())
        last_modified = os.stat(kgsPath)[-2]
        if last_update > last_modified:
            logging.info("Site is up to date.")
            return

    # Save the last generation date-time.
    # Note: We want to do this operation first, since it might take longer to
    # generate the site than the scheduler's wait time.
    open(timestampPath, 'w').write(str(time.time()))

    # Copy the KGS config file to a versioned version
    shutil.copy(
        kgsPath, os.path.join(siteDir, 'controlled-packages-%s.cfg' %ver))

    # Create the buildout config file and version it
    buildoutPath = os.path.join(siteDir, 'buildout.cfg')
    logging.info("Generating buildout config: %s" % buildoutPath)
    buildout.generateBuildout(kgsPath, buildoutPath)
    shutil.copy(buildoutPath, os.path.join(siteDir, 'buildout-%s.cfg' %ver))

    # Create a versions config file and version it
    versionsPath = os.path.join(siteDir, 'versions.cfg')
    logging.info("Generating version config file: %s" % versionsPath)
    version.generateVersions(kgsPath, versionsPath)
    shutil.copy(versionsPath, os.path.join(siteDir, 'versions-%s.cfg' %ver))

    # Create a links config file and version it
    linksPath = os.path.join(siteDir, 'links.html')
    link.generateLinks(kgsPath, linksPath)
    shutil.copy(linksPath, os.path.join(siteDir, 'links-%s.html' %ver))

    # Update the full index (which is assumed to live in the site directory)
    logging.info("updating the index")
    ppix.generatePackagePages(kgsPath, siteDir)

    # Update the minimal index
    logging.info("updating the minimal index")
    midxDir = os.path.join(siteDir, 'minimal')
    if not os.path.exists(midxDir):
        os.mkdir(midxDir)
    ppix.generatePackagePages(kgsPath, midxDir)
    ppix.generateIndexPage(kgsPath, midxDir)
    midxVerDir = os.path.join(siteDir, 'minimal-%s' %ver)
    if os.path.exists(midxVerDir):
        shutil.rmtree(midxVerDir)
    shutil.copytree(midxDir, midxVerDir)

    # copy over the resource files
    resourcesDir = os.path.join(siteDir, 'resources')
    logging.info("copying resource files to %s" % resourcesDir)
    if os.path.exists(resourcesDir):
        shutil.rmtree(resourcesDir)
    shutil.copytree(RESOURCES_PATH, resourcesDir)

    # Update the intro page
    logging.info("updating the intro page")
    intro.main(['-d',siteDir])

    logging.info("finished generating site.")


parser = optparse.OptionParser()
parser.add_option("-s","--site-dir", action="store",
                  type="string", dest="siteDir", metavar="DIR",
                  help="The directory where the site should be generated")

def main(args=None):
    logging.basicConfig(level=logging.INFO)

    if args is None:
        args = sys.argv[1:]
    if not args:
        args = ['-h']

    options, args = parser.parse_args(args)
    if not options.siteDir:
        logging.error("You must specify the site directory with the -s option.")
        sys.exit(1)

    siteDir = os.path.abspath(options.siteDir)

    generateSite(siteDir)
