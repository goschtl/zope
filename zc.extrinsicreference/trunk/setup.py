##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Setup for zc.extrinsicreference package
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zc.extrinsicreference',
    version='0.4.0dev',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    description='Extrinsic reference registries',
    long_description=(
        read('README.txt')
        + '\n\n' +
        'Detailed Documentation\n' +
        '----------------------'
        + '\n\n' +
        read('src', 'zc', 'extrinsicreference', 'README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license='ZPL 2.1',
    keywords='extrinsic key reference zope zope3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    url='http://pypi.python.org/pypi/zc.extrinsicreference',
    packages=find_packages('src'),
    package_dir={'':'src'},
    namespace_packages=['zc'],
    install_requires=[
        'ZODB3',
        'setuptools',
        'zc.shortcut',
        'zope.app.keyreference',
        'zope.component',
        'zope.interface',
        'zope.testing',
        ],
    include_package_data=True,
    zip_safe=False,
    )
