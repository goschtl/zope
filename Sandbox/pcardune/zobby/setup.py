##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: setup.py 72 2007-03-26 15:31:12Z rineichen $
"""

import os
import site
import sys
import zipfile

application = 'Zope3'
sources = 'src'
precompiled = 'Zope3-pyd-Py-2.4.3-Development-Revision-73085.zip'
here = os.path.dirname(os.path.abspath(__file__))
application_path = os.path.join(here, application)
precompiled_path = os.path.join(here, precompiled)
zopeskel = [application_path, 'zopeskel' ,'etc']
buildsupport = os.path.join(application_path, 'buildsupport')


if '-q' in sys.argv or '--quiet' in sys.argv:
    verbose = False
else:
    verbose = True

if '--dry-run' in sys.argv or '-n' in sys.argv:
    dry_run = True
else:
    dry_run = False

def _remove_file(path):
    try:
        if not dry_run:
            os.remove(path)

        if verbose:
            print 'removing', path

    except:
        pass # there is no file to remove

def _remove_pyc(ignore, dirname, files):
    # remove and remember removed files
    [_remove_file(os.path.join(dirname, file)) 
     for file in files if file.endswith('.pyc') or file.endswith('.pyd')]

if verbose:
    print 'running *.pyc clean-up'
# remove *.pyc from sources
os.path.walk(os.path.join(here, sources), _remove_pyc, None)
os.path.walk(os.path.join(application_path, sources), _remove_pyc, None)

# remove *.zcml from package-includes
if verbose:
    print 'running package-includes clean-up'
path = list(zopeskel);
path.append('package-includes')
path = os.path.join(*path)
[_remove_file(os.path.join(path, file))
 for file in os.listdir(path) if file.endswith('.zcml')]


path = list(zopeskel); path.append('securitypolicy.zcml')
path = os.path.join(*path)
_remove_file(path)

# Add 'buildsupport' to sys.path and process *.pth files from 'buildsupport':
last = len(sys.path)
site.addsitedir(buildsupport)
if len(sys.path) > last:
    # Move all appended directories to the start.
    # Make sure we use ZConfig shipped with the distribution
    new = sys.path[last:]
    del sys.path[last:]
    sys.path[:0] = new

import zpkgsetup.package
import zpkgsetup.publication
import zpkgsetup.setup

context = zpkgsetup.setup.SetupContext(
    'Zope', '3.2.X', __file__)

context.load_metadata(
    os.path.join(application_path, 'releases', 'Zope',
                 zpkgsetup.publication.PUBLICATION_CONF))

context.walk_packages(sources)
context.walk_packages(os.path.join('.', application, sources))

context.setup()
# add pyc's if nessecary
if os.path.exists(precompiled_path) and 'build_ext' not in sys.argv and sys.platform == 'win32' :
    zip = zipfile.ZipFile(precompiled_path)
    if verbose:
        print 'copying precompiled extension'

    for name in zip.namelist():
        path = os.path.join(application_path, *name.split('/'))
        open(path, 'wb').write(zip.read(name))
        if verbose:
            print 'copying ', path
        
    zip.close()

if os.path.exists(precompiled_path) and verbose:
    print 'done'

if not os.path.exists(precompiled_path):
    print ""
    print "********************************"
    print "ALERT, *.pyd zip file is missing"
    print "********************************"
    print ""
