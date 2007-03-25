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
"""Setup for zope.app.appsetup package

$Id$
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.app.appsetup',
      version='3.4dev',
      url='http://svn.zope.org/zope.app.appsetup',
      license='ZPL 2.1',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
	  packages=find_packages('src'),
	  package_dir = {'': 'src'},
      extras_require=dict(test=['zope.app.testing']),
      namespace_packages=['zope', 'zope.app'],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.security',
                        'zope.component',
                        'zope.app.component',
                        'zope.configuration',
                        'zope.event',
                        'zope.traversing',
                        'zope.app.container',
                        'zope.app.publication',
                        'ZODB3',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
