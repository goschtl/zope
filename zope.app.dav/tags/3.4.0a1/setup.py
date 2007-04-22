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
"""Setup for zope.app.dav package

$Id$
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.dav',
      version = '3.4.0a1',
      url='http://svn.zope.org/zope.app.dav',
      license='ZPL 2.1',
      description='Zope dav',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles']),
      install_requires=['setuptools',
                        'ZODB3',
                        'zope.annotation',
                        'zope.app.container',
                        'zope.app.file',
                        'zope.app.folder',
                        'zope.app.form',
                        'zope.component',
                        'zope.configuration',
                        'zope.dublincore',
                        'zope.event',
                        'zope.filerepresentation',
                        'zope.interface',
                        'zope.lifecycleevent',
                        'zope.location',
                        'zope.pagetemplate',
                        'zope.publisher',
                        'zope.schema',
                        'zope.size',
                        'zope.traversing',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
