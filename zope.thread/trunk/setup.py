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
"""Setup for zope.thread package

$Id$
"""

import os

from setuptools import setup, Extension, find_packages

setup(name='zope.thread',
      version='3.3dev',
      url='http://svn.zope.org/zope.thread',
      license='ZPL 2.1',
      description='Zope3 Thread-Local Storage',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description='This package supplies a mechoanism for storing '
                       '"thread-local" values, such as the site manager '
                       'discovered during URL traversal.',
      
      packages=find_packages('src'),
      package_dir = {'': 'src'},

      ext_modules=[Extension("zope.thread._zope_thread",
                             [os.path.join('src', 'zope', 'thread',
                                           "_zope_thread.c")
                              ]),
                   ],

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=[],
      include_package_data = False,

      zip_safe = False,
      )
