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
"""Setup for zope.location package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name='zope.location',
      version='3.4dev',
      url='http://svn.zope.org/zope.location',
      license='ZPL 2.1',
      description='Zope Proxies',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="In Zope3, location are special objects"
                       "that has a structural location.",

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['zope.interface',
                        'zope.component',
                        'zope.proxy',
                        'zope.schema',
                        'zope.testing',
                        'zope.traversing',
                        'zope.app.component'],
      include_package_data = True,

      zip_safe = False,
      )
