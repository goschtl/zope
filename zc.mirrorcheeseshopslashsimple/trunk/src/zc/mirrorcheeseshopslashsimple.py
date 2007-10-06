##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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

import ConfigParser
import os, sys, time, urllib, urllib2, xmlrpclib
import zc.lockfile

lock_file_path = 'pypy-poll-access.lock'
poll_time_path = 'pypy-poll-timestamp'
controlled_packages_path = 'controlled-packages.cfg'

simple = "http://cheeseshop.python.org/simple/"

def get_dest_dir(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) != 1:
        print "Usage: update dest"
        sys.exit(1)

    return os.path.abspath(args[0])

def get_page(dest, package, force=False):
    try:
        pdest = os.path.join(dest, package)
    except UnicodeEncodeError:
        print 'skipping %r which has a non-ascii name' % `package`
        return

    if os.path.exists(pdest):
        if not force:
            assert os.path.isdir(pdest)
            print 'Skipping existing', `package`
            return
    else:
        os.mkdir(pdest)

    try:
        upackage = urllib.quote(package)
    except KeyError:
        print 'skipping %r which has a non-ascii name' % `package`
        return

    try:
        page = urllib2.urlopen(simple+upackage+'/').read()
    except urllib2.HTTPError, v:
        if '404' in str(v):             # sigh
            print 'Skipping', `package`, "which isn't on the original site."
            return

    write(page, pdest, 'index.html')

def get_controlled_pacakges(dest):
    cpath = os.path.join(dest, controlled_packages_path)
    if not os.path.exists(cpath):
        return ()
    config = ConfigParser.RawConfigParser()
    config.read(cpath)
    return tuple(config.sections())

def save_time(dest, timestamp):
    open(os.path.join(dest, poll_time_path), 'w').write(
        "%s\n" % int(timestamp)
        )

def create(dest):
    print 'Creating initial mirror.'
    start = time.time()
    server = xmlrpclib.Server('http://cheeseshop.python.org/pypi')
    packages = server.list_packages()
    for package in packages:
        print `package`
        get_page(dest, package, True)

    save_time(dest, start-86400)

def write(page, *dest):
    dest = os.path.join(*dest)
    open(dest+'t', 'w').write(page)
    if os.path.exists(dest):
        os.remove(dest)
    os.rename(dest+'t', dest)

def update(args=None):

    dest = get_dest_dir(args)

    lock = zc.lockfile.LockFile(os.path.join(dest, lock_file_path))
    try:
        ptp = os.path.join(dest, poll_time_path)
        if not os.path.exists(ptp):
            create(dest)

        last = int(open(ptp).read().strip())

        # get updated packages:
        server = xmlrpclib.Server('http://cheeseshop.python.org/pypi')
        packages = sorted((
            (timestamp, name)
            for (name, version, timestamp, action)
            in server.changelog(last)
            ))
        packages = dict((
            (name, timestamp)
            for (timestamp, name)
            in packages
            ))
        packages = sorted((
            (timestamp, name)
            for (name, timestamp)
            in packages.items()
            ))

        # Ignore all packages that are controlled
        controlled_packages = get_controlled_pacakges(dest)
        packages = sorted((
            (timestamp, name)
            for (timestamp, name) in packages
            if name not in controlled_packages
            ))

        if packages:
            print 'Update packages: ' + ', '.join([n for (t, n) in packages])

        for timestamp, name in packages:
            get_page(dest, name, True)
            save_time(dest, timestamp)

        # If there were any, then update the index:
        if packages:
            index = sorted((
                (n.lower(), n) for n in os.listdir(dest)
                if os.path.isdir(os.path.join(dest, n))
                ))
            page = (
                '<html><head><title>Simple Index</title></head><body>\n' +
                '\n'.join([
                    ("<a href='%s/'>%s</a><br/>" % (urllib.quote(n), n))
                    for (l, n) in index
                    ])
                 + '\n</body></html>\n'
                )
            write(page, dest, 'index.html')

    finally:
        lock.close()

def generate_buildout(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) != 2:
        print "Usage: dest index_url"
        sys.exit(1)

    dest = os.path.abspath(args[0])
    index_url = args[1]

    # Extract a list of all packages that need to be tested and record the
    # version to be tested. By default this version is the last available one.
    cpath = os.path.join(dest, controlled_packages_path)
    config = ConfigParser.RawConfigParser()
    config.read(cpath)
    packages = []
    for section in config.sections():
        packages.append((
            section,
            config.get(section, 'versions').split()[-1],
            config.getboolean(section, 'tested')
            ))

    # Create the data dictionary
    data = {
        'index_url': index_url,
        'tested-packages': '\n    '.join([p for (p, v, t) in packages if t]),
        'versions': '\n'.join([p + ' = ' + v for (p, v, t) in packages])
        }

    # Write a new buildout.cfg file
    buildoutcfg_path = os.path.join(dest, 'buildout.cfg')
    templ_path = os.path.join(os.path.dirname(__file__), 'buildout.cfg.in')
    open(buildoutcfg_path, 'w').write(
        open(templ_path, 'r').read() %data)


def generate_controlled_pages(args=None):
    dest = get_dest_dir(args)
    cpath = os.path.join(dest, controlled_packages_path)
    config = ConfigParser.RawConfigParser()
    config.read(cpath)

    server = xmlrpclib.Server('http://cheeseshop.python.org/pypi')

    templ = ('<html><head><title>Links for "%(package)s"</title></head>'
             '<body><h1>Links for "%(package)s"</h1>%(links)s</body></html>')

    link_templ = '<a href="%(url)s#md5=%(md5_digest)s">%(filename)s</a><br/>'

    for package in config.sections():
        print package
        package_path = os.path.join(dest, package)
        links = []
        for version in config.get(package, 'versions').split():
            dist_links = server.package_urls(package, version)
            for link in dist_links:
                links.append(link_templ %link)
        if links:
            open(os.path.join(package_path, 'index.html'), 'w').write(
                templ %{'package': package, 'links': '\n'.join(links)})
        else:
            # A small fallback, in case PyPI does not maintain the release
            # files.
            get_page(dest, package, True)
