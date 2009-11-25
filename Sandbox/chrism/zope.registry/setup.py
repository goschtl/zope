##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################

"""Setup for zope.registry package

$Id: setup.py 105736 2009-11-16 22:34:23Z kobold $
"""

import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='zope.registry',
    version = '0.0',
    url='http://pypi.python.org/pypi/zope.registry',
    license='ZPL 2.1',
    description='Zope Component Architecture',
    author='Zope Corporation and Contributors',
    author_email='zope-dev@zope.org',
    long_description='long description',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['zope',],
    tests_require = [
        'zope.testing'
        ],
    install_requires=['setuptools',
                      'zope.interface',
                      'zope.event',
                      ],
    include_package_data = True,
    zip_safe = False,
    )
