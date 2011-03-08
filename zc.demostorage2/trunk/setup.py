##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

from setuptools import setup, find_packages

def read(rname):
    return open(os.path.join(os.path.dirname(__file__), *rname.split('/')
                             )).read()

long_description = '\n\n'.join((
    read('README.txt'),
    read('CHANGES.txt'),
    read('src/zc/demostorage2/README.txt'),
    'Download\n'
    '--------\n',
    ))

open('doc.txt', 'w').write(long_description)

setup(
    name = 'zc.demostorage2',
    version = '0.2.0dev',
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'ZODB storage that stores changes relative to a base storage',
    long_description=long_description,
    license = 'ZPL 2.1',

    include_package_data = True,
    packages = find_packages('src'),
    namespace_packages = ['zc'],
    package_dir = {'': 'src'},
    install_requires = [
        'ZODB3',
        'setuptools',
        ],
    extras_require=dict(
        test=[
            'zope.testing',
            ]),
    zip_safe = False,
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Framework :: ZODB',
       ],
    )
