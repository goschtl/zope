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
"""Setup for zope.i18nmessageid package

$Id$
"""
import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.browserzcml2',
      version='3.2',
      url='http://svn.zope.org/zope.browserzcml2',
      license='ZPL 2.1',
      description='Alternate, non-magical browser ZCML directives',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description='',
      
      packages=['zope', 'zope.browserzcml2'],
      package_dir = {'': 'src'},

      namespace_packages=['zope'],
      tests_require = ['zope.testing'],
      install_requires=['zope.app', 'zope.configuration', 'zope.formlib',
                        'zope.publisher'],
      include_package_data = True,

      zip_safe = False,
      )
