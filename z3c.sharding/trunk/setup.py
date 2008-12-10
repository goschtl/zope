##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""Package setup.

$Id: setup.py 17 2008-02-27 09:29:05Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='z3c.sharding',
    version = '0.1.0-dev',
    author='Keas, Inc.',
    description='Database Sharding for ZODB',
    long_description=(
        read('README.txt')
        + '\n\n' +
        read('CHANGES.txt')
        ),
    license = "ZPL-2.1",
    keywords = "ZODB sharding",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages = ['z3c'],
    extras_require=dict(
        test=['zope.app.testing',
              'zope.testing',],
        ),
    install_requires=[
        'setuptools',
        ],
    include_package_data = True,
    zip_safe = False,
    )
