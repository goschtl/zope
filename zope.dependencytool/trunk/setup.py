##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for zope.dependencytool package

$Id: setup.py 72841 2007-02-26 22:25:58Z ctheune $
"""

import os

from setuptools import setup, find_packages

setup(name='zope.dependencytool',
      version='3.4.0b1',
      url='http://svn.zope.org/zope.dependencytool',
      license='ZPL 2.1',
      description='Zope dependencytool',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="Find dependencies of a package or module.",

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=[],
      include_package_data = True,

      zip_safe = False,
      )
