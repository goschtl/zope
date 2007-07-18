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

import marshal, os, re, sys, time, traceback
import urllib, urllib2, urlparse, xmlrpclib
import mechanize, setuptools.package_index
import zc.lockfile

pound_egg_link = re.compile('[a-z+]+://\S+#egg=\S+')
repo_py_version = re.compile('\d+[.]\d+/').match
repo_general = 'source/', 'any/'
packages = "http://cheeseshop.python.org/packages/"
lock_file_path = 'pypy-poll-access.lock'
poll_time_path = 'pypy-poll-timestamp'

repos = None

def get_urls(name):
    urls = {}
            
    browser = mechanize.Browser()

    global repos
    if repos is None:
        browser.open(packages)
        repos = [link.url for link in browser.links()
                 if (link.url in repo_general) or repo_py_version(link.url)]

    versions = set()
    for repo in repos:
        folder = packages+repo+name[0]+'/'+name+'/'
        try:
            browser.open(folder)
        except urllib2.HTTPError:
            continue
        for link in browser.links():
            url = link.url
            if ('/' in url) or ('?' in url):
                continue
            urls[folder+url] = url, None, None
            for dist in setuptools.package_index.distros_for_location(
                folder+url, url):
                try:
                    version = dist.version
                    if version:
                        versions.add(version)
                except ValueError:
                    pass

    server = xmlrpclib.Server('http://cheeseshop.python.org/pypi')
    for version in versions:
        for url_data in server.release_urls(name, version):
            url = url_data['url']
            if url in urls:
                urls[url] = urls[url][0], None, url_data.get('md5_digest')
            else:
                urls[url] = url, None, url_data.get('md5_digest')
                
    releases = server.package_releases(name)
    for release in releases:
        data = server.release_data(name, release)
        for text, meta in (('download_url', 'download'),
                           ('home_page', 'homepage'),
                           ):
            url = data.get(text, '')
            if url == 'UNKNOWN':
                continue
            if url:
                urls[url] = '%s %s' % (release, text), meta, None
        for url in pound_egg_link.findall(data.get('description') or ''):
            urls[url] = url, None, None

    return urls

def get_page(dest, package, force=False):
    try:
        pdest = os.path.join(dest, package)
    except UnicodeEncodeError:
        print 'skipping %r which has a non-ascii name' % `package`
        return

    if (not force) and os.path.exists(pdest):
        assert os.path.isdir(pdest)
        print 'Skipping existing', `package`
        return

    urls = get_urls(package)
    traceback.print_exc()
    if not os.path.isdir(pdest):
        os.mkdir(pdest)
    marshal.dump(urls, open(os.path.join(pdest, 'urls.mar'), 'w'))
    output_package(package, urls, pdest)

def save_time(dest, timestamp):
    open(os.path.join(dest, poll_time_path), 'w').write(
        "%s\n" % int(timestamp)
        )

def get_all_pages(dest, force=False):
    assert os.path.isdir(dest)
    timestamp_path = os.path.join(dest, poll_time_path)
    if not os.path.exists(os.path.join(dest, poll_time_path)):
        save_time(time.time())

    server = xmlrpclib.Server('http://cheeseshop.python.org/pypi')
    packages = server.list_packages()
            
    for package in packages:
        print `package`
        try:
            get_page(dest, package, force)
        except:
            print 'Error getting', `package`
            traceback.print_exc()
            
    print 'Done'

def output_package(name, urls, dest):

    urls = sorted((
        (url, urls[url])
        for url in urls
        if non_pypi_home(url, name)
        ))
    
    page = template % (
        name, name,
        "\n  ".join([
        '<p><a%s href="%s%s">%s</a></p>' %
        (meta and (' meta="%s"' % meta) or '',
         url,
         md5 and ("#md5="+md5) or '',
         title)
        for (url, (title, meta, md5)) in urls
        ])
        )
            
    open(os.path.join(dest, 'index.html'), 'w').write(page)

_pypi_names = 'python.org', 'www.python.org', 'cheeseshop.python.org'
def non_pypi_home(url, package):
    protocol, host, path, parms, query, frag = urlparse.urlparse(url)
    if ((host not in _pypi_names) or (protocol != 'http') or parms
        or query or frag
        ):
        return True
    if path[-1] == '/':
        path = path[:-1]
    if path == "/pypi/"+package:
        return False
    return True
            
template = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
  <title>Links for %s</title>
<head>
</head>
<body>
  <h1>Links for %s</h1>

  %s
  
</body>
</html>
"""

def rerender_all(dest):
    for d in os.listdir(dest):
        mar = os.path.join(dest, d, 'urls.mar')
        if os.path.exists(mar):
            try:
                urls = marshal.load(open(mar))
            except ValueError:
                traceback.print_exc()
            else:
                output_package(d, urls, os.path.join(dest, d))

def update(dest):
    lock = zc.lockfile.LockFile(os.path.join(dest, lock_file_path))
    try:
        last = int(open(os.path.join(dest, poll_time_path)).read().strip())
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
        for timestamp, name in packages:
            print timestamp, name
            get_page(dest, name, True)
            save_time(dest, timestamp)
    finally:
        lock.close()
                                   
    
