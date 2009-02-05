##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""HTTP Form Data Parser setup

$Id$
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (read('README.txt') +
                    '\n\n' +
                    read('CHANGES.txt'))

setup(
    name='zope.httpform',
    version='1.0dev',
    url='http://pypi.python.org/pypi/zope.httpform',
    license='ZPL 2.1',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description="HTTP Form Data Parser",
    long_description=long_description,

    # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=['Programming Language :: Python',
                'Environment :: Web Environment',
                'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                'Framework :: Zope3',
                ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'zope.interface',
        ],
    )
