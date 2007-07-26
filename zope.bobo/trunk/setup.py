##############################################################################
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for zope.bobo package

$Id$
"""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'zope.bobo'
setup(
    name=name,
    version = '0.1',
    url='http://www.python.org/pypi/'+name,
    license='ZPL 2.1',
    description='Zope minimal object publishing',
    author='Zope Corporation and Contributors',
    author_email='zope3-dev@zope.org',
    long_description=(
        read('README.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src', 'zope', 'bobo', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
    packages = find_packages('src'),
    package_dir = {'': 'src'},

    namespace_packages=['zope',],
    tests_require = ['zope.testing'],
    install_requires=['zope.interface',
                      'zope.publisher',
                      'zope.event',
                      'zope.component',
                      'zope.security',
                      'setuptools',
                      ],
    include_package_data = True,
    zip_safe = False,
    )
