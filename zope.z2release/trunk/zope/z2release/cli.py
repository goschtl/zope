"""
Generate an index file based on the version.cfg file of Zope 2
in order to provide a version specific index page generated to be used
in combination with easy_install -i <some_url>

Usage:

cli.py tags/2.12.0a3 /tmp/index/2.12.0a3
cli.py branches/2.12 /tmp/index/2.12

"""

import os
import sys
import urllib
from xmlrpclib import Server

from zope.z2release.utils import CasePreservingConfigParser
from zope.z2release.utils import write_index


def fetch_cfg(url, version_file):
    print >>sys.stderr, 'Fetching %s' % url
    data = urllib.urlopen(url).read()
    file(version_file, 'w').write(data)


def write_versions(CP, server, dirname):
    for package in CP.options('versions'):
        version = CP.get('versions', package)
        if '#' in version:
            version = version.split('#')[0].strip()
        write_index(server, package, version, dirname)


def main():
    if len(sys.argv) != 3:
        print 'Usage: z2_kgs <tag-name> <destination-dirname>'
        print 'Example: z2_kgs tags/2.12.1 /var/www/download.zope.org/Zope2/index/2.12.1/'
        sys.exit(1)

    tag = sys.argv[1]
    dirname = sys.argv[2]
    if not os.path.exists(dirname):
        print >>sys.stderr, 'Creating index directory: %s' % dirname
        os.makedirs(dirname)

    server = Server('http://pypi.python.org/pypi')

    version = tag.split('/')[-1]
    versions_url = 'http://svn.zope.org/*checkout*/Zope/%s/versions.cfg' % tag
    version_file = os.path.join(dirname, 'versions.cfg')
    fetch_cfg(versions_url, version_file)

    CP = CasePreservingConfigParser()
    CP.read(version_file)
    write_index(server, 'Zope2', version, dirname)
    write_versions(CP, server, dirname)

    buildout = CP.options('buildout')
    if 'extends' in buildout:
        extends = CP.get('buildout', 'extends')
        if 'http' in extends and extends.endswith('ztk-versions.cfg'):
            ztk_version_file = os.path.join(dirname, 'ztk-versions.cfg')
            fetch_cfg(extends, ztk_version_file)

            CP2 = CasePreservingConfigParser()
            CP2.read(ztk_version_file)
            write_versions(CP2, server, dirname)


if __name__ == '__main__':
    main()
