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
"""Setup for zope.exceptions package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name='zope.exceptions',
      version = '3.4.0b1',
      url='http://svn.zope.org/zope.exceptions',
      license='ZPL 2.1',
      description='Zope Exceptions',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="This package contains exception interfaces "
                       "and implementations which are so general purpose "
                       "that they don't belong in a Zope application-specific "
                       "package.",
      
      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['setuptools',
                        'zope.deprecation',
                        'zope.interface',
                       ],
      include_package_data = True,

      zip_safe = False,
      )
