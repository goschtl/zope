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
"""Setup for zope.app.tree package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name = 'zope.app.tree',
      version = '3.4.0b1',
      url = 'http://svn.zope.org/zope.app.tree',
      license = 'ZPL 2.1',
      description = 'Zope app.tree',
      author = 'Zope Corporation and Contributors',
      author_email = 'zope3-dev@zope.org',
      long_description = "",

      packages = find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages = ['zope', 'zope.app'],
      install_requires = ['setuptools',
                          'zope.app.component',
                          'zope.app.container',
                          'zope.app.folder',
                          'zope.app.rotterdam',
                          'zope.app.skins',
                          'zope.app.testing',
                          'zope.app.zapi',
                          'zope.component',
                          'zope.interface',
                          'zope.location',
                          'zope.publisher',
                          'zope.schema',
                          'zope.security',
                          'zope.testing',
                          'zope.traversing',
                          ],
      include_package_data = True,

      zip_safe = False,
      )
