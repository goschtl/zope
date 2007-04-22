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
"""Setup for zope.app.keyreference package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name = 'zope.app.keyreference',
      version = '3.4dev',
      url = 'http://svn.zope.org/zope.app.keyreference',
      license = 'ZPL 2.1',
      description = 'Zope app.keyreference',
      author = 'Zope Corporation and Contributors',
      author_email = 'zope3-dev@zope.org',
      long_description = '',

      packages = find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages = ['zope', 'zope.app'],
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.component',
                          'zope.i18nmessageid',
                          'zope.interface',
                          'zope.schema',
                          'zope.testing',
                          ],
      include_package_data = True,
      zip_safe = False,
      )
