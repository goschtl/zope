##############################################################################
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
    
def source_release(args=None):
    if args is None:
        args = sys.argv[1:]
    [url, config] = args
    name = url.split('/')[-1]
    t1 = tempfile.mkdtemp('source-release1')
    t2 = tempfile.mkdtemp('source-release2')
    co1 = os.path.join(t1, name)
    co2 = os.path.join(t2, name)
    here = os.getcwd()
    try:

        if url.startswith('file://'):
            shutil.copytree(urlparse.urlparse(url)[2], co1)
        else:
            system('svn', 'export', url, co1)
        shutil.copytree(co1, co2)
        cache = os.path.join(co2, 'release-distributions')
        os.mkdir(cache)
        buildout = zc.buildout.buildout.Buildout(
            os.path.join(co1, config),
            [('buildout', 'download-cache', cache),
             ('buildout', 'verbosity', '10'),
             ],
            False, False, 'install',
            )
        buildout.install([])
        os.chdir(here)

        env = pkg_resources.Environment([
            buildout['buildout']['eggs-directory']
            ])
        dists = [env[project][0].location
                 for project in ('zc.buildout', 'setuptools')
                 ]
        eggs = os.path.join(co2, 'eggs')
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

sys.path[0:0] = [
    os.path.join('eggs', dist)
    for dist in %(path)r
    ]
config = %(config)r

import zc.buildout.buildout
zc.buildout.buildout.main([
    '-Uc', config,
    'buildout:download-cache=release-distributions',
    'buildout:install-from-cache=true',
    ]+sys.argv[1:])
"""
