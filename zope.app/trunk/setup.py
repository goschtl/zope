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
"""Setup for zope.app package

$Id$
"""

import os

from setuptools import setup, Extension, find_packages

setup(name='zope.app',
      version='3.4dev',
      url='http://svn.zope.org/zope.app',
      license='ZPL 2.1',
      description='Zope zope.app',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="This package contains all packages under"
                       "zope.app namespace except some very common"
                       "packages which are eggified seperatly.",

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      ext_modules=[Extension("zope.app.container._zope_app_container_contained",
                             [os.path.join("src", "zope", "app", "container",
                                           "_zope_app_container_contained.c")
                              ], include_dirs=['include']),
                   ],

      namespace_packages=['zope', 'zope.app',],
      tests_require = ['zope.testing'],
      install_requires=['ZODB3',
                        'zdaemon',
                        'zodbcode',
                        'zope.annotation',
                        'zope.cachedescriptors',
                        'zope.component',
                        'zope.configuration',
                        'zope.copypastemove',
                        'zope.contenttype',
                        'zope.datetime',
                        'zope.decorator',
                        'zope.deferredimport',
                        'zope.deprecation',
                        'zope.dottedname',
                        'zope.dublincore',
                        'zope.event',
                        'zope.exceptions',
                        'zope.filerepresentation',
                        'zope.formlib',
                        'zope.hookable',
                        'zope.i18n',
                        'zope.index',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.location',
                        'zope.modulealias',
                        'zope.pagetemplate',
                        'zope.proxy',
                        'zope.publisher',
                        'zope.rdb',
                        'zope.schema',
                        'zope.security',
                        'zope.server',
                        'zope.size',
                        'zope.tal',
                        'zope.tales',
                        'zope.testbrowser',
                        'zope.thread',
                        'zope.traversing',
                        'zope.structuredtext',
                        'RestrictedPython'],
      include_package_data = True,

      zip_safe = False,
      )
