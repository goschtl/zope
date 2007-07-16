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

import marshal, mechanize, os, re, traceback, urllib, urllib2, xmlrpclib

pound_egg_link = re.compile('[a-z+]+://\S+#egg=\S+')
repo_py_version = re.compile('\d+[.]\d+/').match
repo_general = 'source/', 'any/'
packages = "http://cheeseshop.python.org/packages/"

def get_urls(name):
    urls = {}
    server = xmlrpclib.Server('http://cheeseshop.python.org/pypi')
    releases = server.package_releases(name)
    for release in releases:
        data = server.release_data(name, release)
        for text in ('download_url', 'home_page'):
            url = data.get(text, '')
            if url == 'UNKNOWN':
                continue
            if url:
                urls[url] = text
        for url in pound_egg_link.findall(data.get('description') or ''):
            urls[url] = url
    browser = mechanize.Browser()
    browser.open(packages)
    repos = [link.url for link in browser.links()
             if (link.url in repo_general) or repo_py_version(link.url)]

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
            urls[folder+url] = url

    return urls

def get_all_data(start=None):
    data = open('data.mar', 'a')
    server = xmlrpclib.Server('http://cheeseshop.python.org/pypi')
    packages = server.list_packages()
    if start:
        while packages[0] != start:
            packages.pop(0)
            
    for package in packages:
        print package
        try:
            marshal.dump((package, get_urls(package)), data)
        except:
            traceback.print_exc()

def output(filename, dirname):
    f = open(filename)
    while 1:
        try:
            name, urls = marshal.load(f)
        except EOFError:
            break
        except ValueError:
            continue
        d = os.path.join(dirname, name)
        if not os.path.isdir(d):
            os.mkdir(d)
        urls = sorted(urls.items())
        open(os.path.join(d, 'index.html'), 'w').write(
            template % (
            name, name,
            "\n  ".join([
              '<p><a href="%s">%s</a></p>' % (urllib.quote(url), title)
              for (url, title) in urls
              ])
            ))


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
