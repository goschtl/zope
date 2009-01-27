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

formatter = logging.Formatter('%(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger('info')
logger.addHandler(handler)
logger.setLevel(logging.ERROR)

def generateSite(siteDir, templateDir, force=False):
    # Create some important variables
    kgsPath = os.path.join(siteDir, 'controlled-packages.cfg')
    set = kgs.KGS(kgsPath)
    ver = set.version
    logger.info(
        "Building site for version %s using config: %s" % (ver, kgsPath))

    timestampPath = os.path.join(siteDir, TIMESTAMP_FILENAME)

    # If there have been no changes in the file since the last generation,
    # simple do not do anything.
    if os.path.exists(timestampPath):
        last_update = float(open(timestampPath, 'r').read())
        last_modified = os.stat(kgsPath)[-2]
        if last_update > last_modified:
            logger.info("Site is up to date.  Use --force "
                        "on the command line to force a rebuild.")
            if not force:
                return
            else:
                logger.info("Site is up to date, but a rebuild has been forced.")

    # Save the last generation date-time.
    # Note: We want to do this operation first, since it might take longer to
    # generate the site than the scheduler's wait time.
    open(timestampPath, 'w').write(str(time.time()))

    # Create a directory for the new version
    versionDir = os.path.join(siteDir, ver)
    if os.path.exists(versionDir):
        if force:
            shutil.rmtree(versionDir)
        else:
            logger.error("The directory %s already exists.  Use --force to overwrite it." % versionDir)
            return
    os.mkdir(versionDir)

    # Copy the KGS config file, changelog and announcement file to the version
    # directory
    shutil.move(kgsPath, versionDir)
    if set.changelog:
        shutil.move(kgs.changelog, versionDir)
    if set.announcement:
        shutil.move(kgs.announcement, versionDir)

    # Let's now recreate some of the important variables.
    kgsPath = os.path.join(versionDir, 'controlled-packages.cfg')
    set = kgs.KGS(kgsPath)

    # Create the buildout config file
    buildoutPath = os.path.join(versionDir, 'buildout.cfg')
    logger.info("Generating buildout config: %s" % buildoutPath)
    buildout.generateBuildout(kgsPath, buildoutPath)

    # Create a versions config file and version it
    versionsPath = os.path.join(versionDir, 'versions.cfg')
    logger.info("Generating version config file: %s" % versionsPath)
    version.generateVersions(kgsPath, versionsPath)

    # Create a links config file and version it
    linksPath = os.path.join(versionDir, 'links.html')
    link.generateLinks(kgsPath, linksPath)

    # Update the full index (which is assumed to live in the site directory)
    logger.info("updating the index")
    ppix.generatePackagePages(kgsPath, versionDir)

    # Update the minimal index
    logger.info("updating the minimal index")
    midxDir = os.path.join(versionDir, 'minimal')
    if not os.path.exists(midxDir):
        os.mkdir(midxDir)
    ppix.generatePackagePages(kgsPath, midxDir)
    ppix.generateIndexPage(kgsPath, midxDir)

    # copy over the resource files
    resourcesDir = os.path.join(versionDir, 'resources')
    logger.info("copying resource files to %s" % resourcesDir)
    if os.path.exists(resourcesDir):
        shutil.rmtree(resourcesDir)
    shutil.copytree(os.path.join(templateDir, 'resources'), resourcesDir)

    # Update the intro page
    logger.info("updating the intro page")
    #intro.main(['-d',versionDir])

    logger.info("finished generating site.")


parser = optparse.OptionParser()
parser.add_option("-v","--verbose", action="store_true",
                  dest="verbose", default=False,
                  help="When specified, debug information is created.")
parser.add_option("-s","--site-dir", action="store",
                  type="string", dest="siteDir", metavar="DIR",
                  help="The directory where the site should be generated")
parser.add_option("-t","--template-dir", action="store",
                  type="string", dest="templateDir", metavar="DIR",
                  default=os.path.join(os.path.dirname(__file__), 'templates'),
                  help="The directory where the site templates are located.")
parser.add_option("-f","--force", action="store_true", dest="force",
                  help="For the site to rebuild even if it is already at the latest version.")

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    if not args:
        args = ['-h']

    options, args = parser.parse_args(args)

    if options.verbose:
        logger.setLevel(logging.INFO)

    if not options.siteDir:
        logger.error("You must specify the site directory with the -s option.")
        sys.exit(1)

    siteDir = os.path.abspath(options.siteDir)
    templateDir = os.path.abspath(options.templateDir)
    generateSite(siteDir, templateDir, force=options.force)
