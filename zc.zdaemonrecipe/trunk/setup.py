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
name = 'zc.zdaemonrecipe'
version = '0.3dev'

import os
from setuptools import setup, find_packages

entry_points = '''
[zc.buildout]
default=zc.zdaemonrecipe:Recipe
'''

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('zc', 'zdaemonrecipe', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        )

open('doc.txt', 'w').write(long_description)

setup(
    name = name,
    version = version,
    author = 'Jim Fulton',
    author_email = 'jim@zope.com',
    description = 'ZC Buildout recipe for zdaemon scripts',
    long_description=long_description,
    license = 'ZPL 2.1',
    
    entry_points=entry_points,
    packages = find_packages('.'),
    namespace_packages = ['zc'],
    extras_require = dict(test=['zdaemon', 'zope.testing']),
    install_requires = ['setuptools',
                        'zc.buildout', 'zc.recipe.egg',
                        'ZConfig'],
    zip_safe = False,
    )
