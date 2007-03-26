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
"""Setup for zope.app.i18n package

$Id$
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.i18n',
      version='3.4dev',
      url='http://svn.zope.org/zope.app.i18n',
      license='ZPL 2.1',
      description='Zope i18n',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing']),
      install_requires=['setuptools',
                        'zope.app.component',
                        'zope.app.container',
                        'zope.app.publisher',
                        'zope.component',
                        'zope.configuration',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.security',
                        'ZODB3',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
