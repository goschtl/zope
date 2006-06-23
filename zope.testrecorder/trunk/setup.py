##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Setup for zope.testrecorder package

$Id$
"""
try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.testrecorder',
      version='0.2',

      url='http://svn.zope.org/zope.testrecorder',
      license='ZPL 2.1',
      description='Test recorder for functional tests',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description='',
      
      packages=['zope', 'zope.testrecorder'],
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      package_data = {
          '': ['*.txt', '*.zcml'],
          'zope.testrecorder': ['www/*', 'html/*'],
          },

      zip_safe = False,
      )
