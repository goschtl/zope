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
"""Generate a 'Links' HTML page that can be used as a `find-links` entry in
setuptools.

Usage: %s package-cfg-path [output-links-path]

* ``package-cfg-path``

  This is the path to the controlled packages configuration file.

* ``output-links-path``

  The path of the file under which the generated links file is stored. By
  default it is placed in the package configuration file's directory under the
  name 'links.html'.
"""
import os
import sys
import xmlrpclib
import zope.kgs.kgs

TEMPLATE = ('<html>\n<head>\n'
            '<title>Links for the "%(name)s" KGS (version %(version)s)</title>\n'
            '</head>\n'
            '<body>\n'
            '<h1>Links for the "%(name)s" KGS (version %(version)s)</h1>\n'
            '%(links)s\n'
            '</body>\n'
            '</html>')

LINK_TEMPLATE = '<a href="%(url)s#md5=%(md5_digest)s">%(filename)s</a><br/>'

def generateLinks(packageConfigPath, outputPath, offline=False):
    """Generate a ``buildout.cfg`` from the list of controlled packages."""
    kgs = zope.kgs.kgs.KGS(packageConfigPath)
    server = xmlrpclib.Server('http://pypi.python.org/pypi')

    # Collect all links
    links = []
    if not offline:
        for package in kgs.packages:
            for version in package.versions:
                dist_links = server.package_urls(package.name, version)
                for link in dist_links:
                    links.append(LINK_TEMPLATE %link)

    # Write a new versions.cfg file
    open(outputPath, 'w').write(
        TEMPLATE %{'name': kgs.name,
                   'version': kgs.version,
                   'links': '\n'.join(links)})

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print __doc__ % sys.argv[0]
        sys.exit(1)

    packageConfigPath = os.path.abspath(args[0])

    outputPath = os.path.join(
        os.path.dirname(packageConfigPath), 'links.html')
    if len(args) == 2:
        outputPath = args[1]

    generateLinks(packageConfigPath, outputPath)
