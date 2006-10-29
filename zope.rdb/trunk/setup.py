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
"""Setup for zope.rdb package

$Id$
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.rdb',
      version='3.4-dev',
      url='http://svn.zope.org/zope.rdb',
      license='ZPL 2.1',
      description='Zope rdb',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="Zope RDBMS Transaction Integration."
                       "Provides a proxy for interaction between"
                       "the zope transaction framework and the"
                       "db-api connection.  Databases which want to"
                       "support sub transactions need to implement"
                       "their own proxy.",

      packages=['zope',
                'zope.rdb',
                'zope.rdb.browser',
                'zope.rdb.gadfly',
                'zope.rdb.tests'],
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['persistent',
                        'transaction',
                        'zope.interface',
                        'zope.i18nmessageid',
                        'zope.security',
                        'zope.configuration',
                        'zope.schema',
                        'zope.thread',
                        'zope.app.container'],
      include_package_data = True,

      zip_safe = False,
      )
