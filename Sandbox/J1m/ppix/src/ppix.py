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

import marshal, mechanize, re, traceback, urllib2, xmlrpclib

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
    
