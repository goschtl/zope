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
import util

lock_file_path = 'pypi-poll-access.lock'
poll_time_path = 'pypi-poll-timestamp'
controlled_packages_path = 'controlled-packages.cfg'

simple = "http://pypi.python.org/simple/"

def get_dest_dir(args=None):
    if args is None:
        args = sys.argv[1:]

    if len(args) != 1:
        print "Usage: update dest"
        sys.exit(1)

    return os.path.abspath(args[0])

def get_controlled_packages(dest):
    cpath = os.path.join(dest, controlled_packages_path)
    if not os.path.exists(cpath):
        return ()
    config = ConfigParser.RawConfigParser()
    config.read(cpath)
    return tuple(config.sections())

def get_page(dest, package, force=False):

    if not util.isASCII(package):
        print 'skipping %r which has a non-ascii name' % `package`
        return

    pdest = os.path.join(dest, package)
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
    mirror_package(package, page, dest)

def mirror_package(package, page, dest):
    print package, dest

def save_time(dest, timestamp):
    open(os.path.join(dest, poll_time_path), 'w').write(
        "%s\n" % int(timestamp)
        )

def create(dest):
    print 'Creating initial mirror.'
    start = time.time()
    server = xmlrpclib.Server('http://pypi.python.org/pypi')
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
        server = xmlrpclib.Server('http://pypi.python.org/pypi')
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
        controlled_packages = get_controlled_packages(dest)
        packages = sorted((
            (timestamp, name)
            for (timestamp, name) in packages
            if name not in controlled_packages
            ))

        #if packages:
        #    print 'Update packages: ' + ', '.join([n for (t, n) in packages])

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
