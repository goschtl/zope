#############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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

import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urlparse

import pkg_resources

import zc.buildout.buildout

def _system(*args):
    p = subprocess.Popen(args)
    r = p.wait()
    if r:
        raise SystemError("Subprocess failed!")

def _relative(path, to):
    rel = []

    # Remove trailing separators
    while 1:
        d, b = os.path.split(to)
        if b:
            break
        to = d
    
    while path and path != to and path != '/':
        path, base = os.path.split(path)
        if base:
            rel.insert(0, base)
    if path != to:
        return None
    return os.path.join(*rel)
    
def source_release(args=None):
    if args is None:
        args = sys.argv[1:]

    url = args.pop(0)
    config = args.pop(0)

    clopts = []
    for arg in args:
        name, value = arg.split('=', 1)
        section, option = name.split(':')
        clopts.append((section, option, value))
    
    if url.endswith('/'):
        # Remove ending slash
        url = url[:-1]
    url_parts = url.split('/')
    if len(url_parts) > 1 and url_parts[-1] == 'trunk':
        name = url_parts[-2]
    elif len(url_parts) > 2 and url_parts[-2] in ('tags', 'branches'):
        name = url_parts[-3]
        if url_parts[-2] == 'tags':
            name = name + '_' + url_parts[-1]
    else:
        name = url_parts[-1]
    t1 = tempfile.mkdtemp('source-release1')
    t2 = tempfile.mkdtemp('source-release2')
    co1 = os.path.join(t1, name)
    co2 = os.path.join(t2, name)
    here = os.getcwd()
    print 'Creating source release in %s.tgz' % name
    sys.stdout.flush()
    try:

        if url.startswith('file://'):
            shutil.copytree(urlparse.urlparse(url)[2], co1)
        else:
            _system('svn', 'export', url, co1)
        shutil.copytree(co1, co2)
        cache = os.path.join(co2, 'release-distributions')
        os.mkdir(cache)
        buildout = zc.buildout.buildout.Buildout(
            os.path.join(co1, config), clopts,
            False, False, 'bootstrap',
            )
        eggs_directory = buildout['buildout']['eggs-directory']
        reggs = _relative(eggs_directory, co1)
        if reggs is None:
            print 'Invalid eggs directory (perhaps not a relative path)', \
                eggs_directory
            sys.exit(0)

        buildout.bootstrap([])

        args.extend([
            '-Uvc', os.path.join(co1, config),
            'buildout:download-cache='+cache
            ])

        _system(os.path.join(co1, 'bin', 'buildout'), *args)
        
        os.chdir(here)

        env = pkg_resources.Environment([eggs_directory])
        dists = [env[project][0].location
                 for project in ('zc.buildout', 'setuptools')]
                 
        eggs = os.path.join(co2, reggs)
        os.mkdir(eggs)
        for dist in dists:
            if os.path.isdir(dist):
                shutil.copytree(dist,
                                os.path.join(eggs, os.path.basename(dist))
                                )
            else:
                shutil.copy(dist, eggs)


        open(os.path.join(co2, 'install.py'), 'w').write(
            install_template % dict(
                path = [os.path.basename(dist) for dist in dists],
                config = config,
                version = sys.version_info[:2],
                eggs_directory = reggs,
                args = repr(args)[1:-1],
            ))

        
        tar = tarfile.open(name+'.tgz', 'w:gz')
        tar.add(co2, name)
        tar.close()


    finally:
        shutil.rmtree(t1)
        shutil.rmtree(t2)

install_template = """
import os, sys

if sys.version_info[:2] != %(version)r:
    print "Invalid Python version, %%s.%%s." %% sys.version_info[:2]
    print "Python %%s.%%s is required." %% %(version)r
    sys.exit(1)

here = os.path.abspath(os.path.dirname(__file__))

sys.path[0:0] = [
    os.path.join(here, %(eggs_directory)r, dist)
    for dist in %(path)r
    ]
config = os.path.join(here, %(config)r)

import zc.buildout.buildout
zc.buildout.buildout.main([
    %(args)s,
    '-Uc', config,
    'buildout:download-cache='+os.path.join(here, 'release-distributions'),
    'buildout:install-from-cache=true',
    ]+sys.argv[1:])
"""
