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

Usage: %s [-i] package-cfg-path [output-index-path]

* -i

  When set, this flag causes an `index.html` file to be generated that
  provides a link to every package's links page.

* ``package-cfg-path``

  This is the path to the controlled packages configuration file.

* ``output-index-path``

  The path of the directory under which the generated index is stored. By
  default it is placed in the package configuration file's directory under the
  name 'index'.
"""
import os
import sys
import urllib
import urllib2
import xmlrpclib
import zope.kgs.kgs

TEMPLATE = ('<html>\n<head>\n<title>%(title)s</title>\n</head>\n'
            '<body>\n<h1>%(title)s</h1>\n%(body)s\n</body>\n'
            '</html>')

LINK_TEMPLATE = '<a href="%(url)s#md5=%(md5_digest)s">%(filename)s</a><br/>'
SIMPLE_LINK_TEMPLATE = '<a href="%(url)s">%(name)s</a><br/>'

SIMPLE_BASE_URL = "http://pypi.python.org/simple/"

def generatePackagePage(package, destDir, server, offline=False):
    packagePath = os.path.join(destDir, package.name)
    links = []
    if not offline:
        for version in package.versions:
            dist_links = server.package_urls(package.name, version)
            for link in dist_links:
                links.append(LINK_TEMPLATE %link)

    if not os.path.exists(packagePath):
        os.mkdir(packagePath)

    if links or offline:
        open(os.path.join(packagePath, 'index.html'), 'w').write(
            TEMPLATE %{'title': 'Links for "%s"' %package.name,
                       'body': '\n'.join(links)})
    else:
        # A small fallback, in case PyPI does not maintain the release
        # files.
        page = urllib2.urlopen(SIMPLE_BASE_URL + package.name + '/').read()
        open(os.path.join(packagePath, 'index.html'), 'w').write(page)


def generatePackagePages(packageConfigPath, destDir, offline=False):
    kgs = zope.kgs.kgs.KGS(packageConfigPath)
    server = xmlrpclib.Server('http://pypi.python.org/pypi')

    for package in kgs.packages:
        generatePackagePage(package, destDir, server, offline=offline)


def generateIndexPage(packageConfigPath, destDir):
    kgs = zope.kgs.kgs.KGS(packageConfigPath)
    links = []
    for pkg in kgs.packages:
        links.append(
            SIMPLE_LINK_TEMPLATE %{
                'url': urllib.quote(pkg.name), 'name': pkg.name}
            )
    open(os.path.join(destDir, 'index.html'), 'w').write(
        TEMPLATE %{
          'title': 'Simple Index for the "%s" KGS (version %s)' %(kgs.name,
                                                                  kgs.version),
          'body': '\n'.join(links)})


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) < 1:
        print __doc__ % sys.argv[0]
        sys.exit(1)

    createIndex = False
    if args[0] == '-i':
        createIndex = True
        args = args[1:]

    packageConfigPath = os.path.abspath(args[0])

    destDir = os.path.join(
        os.path.dirname(packageConfigPath), 'index')
    if len(args) == 2:
        destDir = args[1]
    if not os.path.exists(destDir):
        os.mkdir(destDir)

    generatePackagePages(packageConfigPath, destDir)

    if createIndex:
        generateIndexPage(packageConfigPath, destDir)
