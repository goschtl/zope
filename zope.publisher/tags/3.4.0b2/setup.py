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
"""Setup for zope.publisher package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name='zope.publisher',
      version = '3.4.0b2',
      url='http://svn.zope.org/zope.publisher',
      license='ZPL 2.1',
      description='Zope publisher',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="Publish Python objects on web servers."
                       "Provide an apply-like facility that"
                       "works with any mapping object.",

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['setuptools',
                        'zope.component',
                        'zope.event',
                        'zope.exceptions',
                        'zope.i18n',
                        'zope.interface',
                        'zope.location',
                        'zope.proxy',
                        'zope.security',
                        'zope.testing',
                        'zope.app.testing',
                        'zope.deprecation',
                        'zope.deferredimport'],
      include_package_data = True,

      zip_safe = False,
      )
