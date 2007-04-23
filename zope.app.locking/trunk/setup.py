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
"""Setup for zope.app.server package

$Id: setup.py 74669 2007-04-23 12:04:26Z ctheune $
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.locking',
      version='3.4dev',
      url='http://svn.zope.org/zope.app.server',
      license='ZPL 2.1',
      description='Zope server',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing', 'zope.testing',
                                  'zope.app.file', 'zope.app.folder', ]),
      install_requires=['setuptools',
                        'zope.security',
                        'zope.app.keyreference',
                        'zope.app.i18n',
                        'zope.interface',
                        'zope.schema',
                        'zope.component',
                        'zope.app.i18n',
                        'ZODB3',
                        'zope.app.zapi',
                        'zope.event',
                        'zope.traversing',
                        'zope.size',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
