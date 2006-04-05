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

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.thread',
      version='1.0',
      url='http://svn.zope.org/zope.thread',
      license='ZPL 2.1',
      description='Zope3 Thread-Local Storage',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description='This package supplies a mechoanism for storing '
                       '"thread-local" values, such as the site manager '
                       'discovered during URL traversal.',
      
      packages=['zope', 'zope.thread'],
      package_dir = {'': os.path.join(os.path.dirname(__file__), 'src')},

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
