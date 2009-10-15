##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Setup for z3c.multifieldindex package

$Id$
"""
import os

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='z3c.multifieldindex',
    version='3.4.1dev',
    url='http://pypi.python.org/pypi/z3c.multifieldindex',
    license='ZPL 2.1',
    description='Multi-field index for zope catalog',
    author='Dan Korostelev and Zope Community',
    author_email='zope-dev@zope.org',
    long_description=\
        read('src', 'z3c', 'multifieldindex', 'README.txt') + \
        '\n\n' + \
        read('CHANGES.txt'),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c'],
    install_requires=[
      'setuptools',
      'zc.catalog',
      'ZODB3',
      'zope.app.catalog',
      'zope.app.container',
      'zope.component',
      'zope.index',
      'zope.interface',
      'zope.schema',
      ],
    extras_require = dict(
        test=[
            'zope.testing',
            ],
        ),
    include_package_data=True,
    zip_safe=False,
    )
