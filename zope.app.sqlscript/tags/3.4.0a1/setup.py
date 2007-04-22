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
"""Setup for zope.app.sqlscript package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name = 'zope.app.sqlscript',
      version = '3.4.0a1',
      url = 'http://svn.zope.org/zope.app.sqlscript',
      license = 'ZPL 2.1',
      description = 'Zope app.sqlscript',
      author = 'Zope Corporation and Contributors',
      author_email = 'zope3-dev@zope.org',
      long_description = "",

      packages = find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages = ['zope', 'zope.app'],
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.annotation',
                          'zope.app.cache',
                          'zope.app.component',
                          'zope.app.container',
                          'zope.app.form',
                          'zope.component',
                          'zope.documenttemplate',
                          'zope.i18nmessageid',
                          'zope.interface',
                          'zope.rdb',
                          'zope.schema',
                          'zope.traversing',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zptpage',
                                  'zope.app.zcmlfiles']),
      include_package_data = True,

      zip_safe = False,
      )
