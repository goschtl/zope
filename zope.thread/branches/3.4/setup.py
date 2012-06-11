##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
      version = '3.4',
      url='http://svn.zope.org/zope.thread',
      license='ZPL 2.1',
      description='Zope3 Thread-Local Storage',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description=
      'This package is deprecated and exists soley for backward compatability.',
      
      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['setuptools'],
      include_package_data = False,
      zip_safe = False,
      )
