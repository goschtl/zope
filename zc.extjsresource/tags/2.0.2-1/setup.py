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
import os, setuptools, shutil, urllib2, zipfile

rname = 'ext-2.0.2'
url_base = 'http://extjs.com/deploy'
version = '2.0.2-1'

dest = os.path.join(os.path.dirname(__file__),
                    'src', 'zc', 'extjsresource', 'extjs')
extpaths = []
if not os.path.exists(dest):
    zip_name = rname + '.zip'
    if not os.path.exists(zip_name):
        x = urllib2.urlopen(url_base+'/'+zip_name).read()
        open(zip_name, 'w').write(x)

    zfile = zipfile.ZipFile(zip_name, 'r')

    prefix = rname + '/'
    lprefix = len(rname)

    for zname in sorted(zfile.namelist()):
        assert zname.startswith(prefix)
        dname = dest + zname[lprefix:]
        if dname[-1:] == '/':
            os.makedirs(dname)
        else:
            open(dname, 'w').write(zfile.read(zname))
            extpaths.append('extjs/'+zname[lprefix:])
else:
    lbase = len(os.path.dirname(dest))+1
    for path, dirs, files in os.walk(dest):
        prefix = path[lbase:]
        for file in files:
            extpaths.append(os.path.join(prefix, file))

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setuptools.setup(
    name = 'zc.extjsresource',
    version = version,
    description = "Zope Packaging of the Ext Javascript library",
    long_description = read('README.txt'),

    packages = ['zc', 'zc.extjsresource'],
    package_dir = {'':'src'},
    include_package_data = True,
    package_data = {'zc.extjsresource': extpaths},
    namespace_packages = ['zc'],
    install_requires = [
        'setuptools',
        'zc.resourcelibrary',
        'zc.extjsresource',
        ],
    zip_safe=False,
    )
