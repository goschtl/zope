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
"""Generates a full KGS site with all bells and whistles."""
import datetime
import docutils.core
import logging
import optparse
import os
import pkg_resources
import re
import shutil
import sys
import time
from zope.kgs import version, buildout, ppix, link, kgs, template

TIMESTAMP_FILENAME = 'cf-timestamp'

FEATURES = [
    ('controlled-packages.cfg', u'Controlled Packages'),
    ('versions.cfg',            u'Versions'),
    ('buildout.cfg',            u'Buildout Configuration'),
    ('links.html',              u'Package Links'),
    ('minimal',                 u'Minimal Index'),
    ('index',                   u'Index'),
    ]

formatter = logging.Formatter('%(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger('info')
logger.addHandler(handler)
logger.setLevel(logging.ERROR)


def _getRenderedFilename(version, filename):
    if not filename:
        return
    return '%s/%s' % (version,
                      os.path.split(filename)[-1].split('.')[0] + '.html')

def _getRenderedTxt(filename):
    if not filename:
        return ""
    f = open(filename)
    parts = docutils.core.publish_parts(source=f.read(), writer_name='html')
    return parts['html_body']

def generateData(src):
    versions = []
    for filename in os.listdir(src):
        path = os.path.join(src, filename)
        if not (os.path.isdir(path) and
                os.path.exists(os.path.join(path, 'controlled-packages.cfg'))):
            continue
        kgsPath = os.path.join(path, 'controlled-packages.cfg')
        set = kgs.KGS(kgsPath)
        features = []
        for (filename, title) in FEATURES:
            if filename in os.listdir(path):
                features.append({'url': '%s/%s' % (set.version, filename),
                                 'title': title})

        files = []
        for filepath in set.files:
            filename = os.path.split(filepath)[-1]
            files.append({
                'url': set.version + '/' + filename,
                'name': filename
                })

        versionData = {
            'name': set.version,
            'date': set.date and str(set.date) or None,
            'features': features,
            'changelog': {
                'url':_getRenderedFilename(set.version, set.changelog),
                'html': _getRenderedTxt(set.changelog)},
            'announcement': {
                'url':_getRenderedFilename(set.version, set.announcement),
                'html': _getRenderedTxt(set.announcement)},
            'files': files,
            }

        versions.append(versionData)
    versions.sort(key=lambda x: pkg_resources.parse_version(x['name']),
                  reverse=True)
    return {'versions': versions,
            'latest': versions[0],
            'title': set.name,
            'siteRoot':''}

def generateSite(siteDir, templateDir, force=False, offline=False,
                 noLinks=False, noIndex=False, noMinimalIndex=False):
    # Create some important variables
    kgsPath = os.path.join(siteDir, 'controlled-packages.cfg')

    # If the `controlled-packages.cfg` file is not found,
    if not os.path.exists(kgsPath):
        logger.info("The site is up-to-date. No new file "
                    "`controlled-packages.cfg` was found.")
        return

    set = kgs.KGS(kgsPath)
    ver = set.version
    logger.info(
        "Building site for version %s using config: %s" % (ver, kgsPath))

    # Create a directory for the new version
    versionDir = os.path.join(siteDir, ver)
    if os.path.exists(versionDir):
        if force:
            logger.info('Recreating directory %s.' %versionDir)
            shutil.rmtree(versionDir)
            os.mkdir(versionDir)
    else:
        os.mkdir(versionDir)

    # Copy the KGS config file, changelog, announcement, and release files to
    # the version directory
    shutil.move(kgsPath, versionDir)
    if set.changelog:
        shutil.move(set.changelog, versionDir)
    if set.announcement:
        shutil.move(set.announcement, versionDir)
    for filepath in set.files:
        shutil.move(filepath, versionDir)

    # Recreate the KGS Path
    kgsPath = os.path.join(versionDir, 'controlled-packages.cfg')

    # Insert date into KGS, if it is not set.
    if not set.date:
        text = open(kgsPath, 'r').read()
        pos = re.search('\[KGS\]\n(?:.+\n)*', text).end()
        text = text[:pos] + 'date = %s\n' %datetime.date.today() + text[pos:]
        open(kgsPath, 'w').write(text)

    # Recreate the KGS
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
    if not noLinks:
        linksPath = os.path.join(versionDir, 'links.html')
        logger.info("generating links")
        link.generateLinks(kgsPath, linksPath, offline=offline)

    # Update the full index (which is assumed to live in the site directory)
    if not noIndex:
        logger.info("updating the index")
        idxDir = os.path.join(versionDir, 'index')
        if not os.path.exists(idxDir):
            os.mkdir(idxDir)
        ppix.generatePackagePages(kgsPath, idxDir, offline=offline)
        ppix.generateIndexPage(kgsPath, idxDir)

    # Update the minimal index
    if not noMinimalIndex:
        logger.info("updating the minimal index")
        midxDir = os.path.join(versionDir, 'minimal')
        if not os.path.exists(midxDir):
            os.mkdir(midxDir)
        ppix.generatePackagePages(kgsPath, midxDir, offline=offline)
        ppix.generateIndexPage(kgsPath, midxDir)

    # Generate Web Site
    logger.info("Generating Web Site")
    template.generateSite(templateDir, siteDir, generateData(siteDir))

    logger.info("finished generating site.")


parser = optparse.OptionParser()
parser.add_option(
    "-q","--quiet", action="store_true",
    dest="quiet", default=False,
    help="When specified, no messages are displayed.")
parser.add_option(
    "-v","--verbose", action="store_true",
    dest="verbose", default=False,
    help="When specified, debug information is created.")
parser.add_option(
    "-s","--site-dir", action="store",
    type="string", dest="siteDir", metavar="DIR",
    help="The directory where the site should be generated")
parser.add_option(
    "-t","--template-dir", action="store",
    type="string", dest="templateDir", metavar="DIR",
    default=os.path.join(os.path.dirname(__file__), 'templates'),
    help="The directory where the site templates are located.")
parser.add_option(
    "-w","--website-only", action="store_true",
    dest="websiteOnly", default=False,
    help="When specified, only the Web site is (re-)generated.")
parser.add_option(
    "-f","--force", action="store_true", dest="force", default=False,
    help=("Force the site to rebuild even if it is already at the "
          "latest version."))
parser.add_option(
    "-o","--offline", action="store_true", dest="offlineMode", default=False,
    help=("Run in offline mode.  Doesn't really do much, good for "
          "developing templates."))
parser.add_option(
    "--no-index", action="store_true", dest="noIndex", default=False,
    help=("When set, no index is created."))
parser.add_option(
    "--no-minimal-index", action="store_true", dest="noMinimalIndex",
    default=False,
    help=("When set, no minimal index is created."))
parser.add_option(
    "--no-links", action="store_true", dest="noLinks", default=False,
    help=("When set, no links file is created."))

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    if not args:
        args = ['-h']

    options, args = parser.parse_args(args)

    if options.verbose:
        logger.setLevel(logging.INFO)
    if options.quiet:
        logger.setLevel(logging.FATAL)

    if not options.siteDir:
        logger.error("You must specify the site directory with the -s option.")
        sys.exit(1)

    siteDir = os.path.abspath(options.siteDir)
    templateDir = os.path.abspath(options.templateDir)

    if options.websiteOnly:
        # Generate Web Site
        logger.info("Generating Web Site")
        template.generateSite(templateDir, siteDir, generateData(siteDir))
        logger.info("finished generating site.")
    else:

        generateSite(
            siteDir, templateDir, options.force, options.offlineMode,
            options.noLinks, options.noIndex, options.noMinimalIndex)
