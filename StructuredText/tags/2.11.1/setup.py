##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Setup for the StructuredText egg package
"""
import os
from setuptools import setup, find_packages, Extension

setup(name='StructuredText',
      version = '2.11.1',
      url='http://cheeseshop.python.org/pypi/StructuredText',
      license='ZPL 2.1',
      description="""\
This package provides the StructuredText package, as known from Zope 2.
Unless you need to communicate with Zope 2 APIs, you're probably
better off using the newer zope.structuredtext module.""",
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=open(
          os.path.join('src', 'StructuredText', 'STNG.txt')).read(),

      packages=find_packages('src'),
      package_dir={'': 'src'},

      install_requires=['zope.structuredtext',
                        'zope.deprecation',
                        ],
      include_package_data=True,
      zip_safe=False,
      )
