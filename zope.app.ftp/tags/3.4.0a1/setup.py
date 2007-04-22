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
"""Setup for zope.app.ftp package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name = 'zope.app.ftp',
      version = '3.4.0a1',
      url = 'http://svn.zope.org/zope.app.ftp',
      license = 'ZPL 2.1',
      description = 'Zope app.ftp',
      author = 'Zope Corporation and Contributors',
      author_email = 'zope3-dev@zope.org',
      long_description = "",

      packages = find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages = ['zope', 'zope.app'],
      install_requires = ['setuptools',
                          'zope.app.container',
                          'zope.component',
                          'zope.copypastemove',
                          'zope.dublincore',
                          'zope.event',
                          'zope.filerepresentation',
                          'zope.interface',
                          'zope.lifecycleevent',
                          'zope.publisher',
                          'zope.security',
                          ],
      extras_require = dict(test=['zope.app.testing',]),
      include_package_data = True,

      zip_safe = False,
      )
