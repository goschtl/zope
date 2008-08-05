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
"""Setup for the Interface egg
"""
import os
from setuptools import setup, find_packages, Extension

setup(name='Interface',
      version = '2.11.1',
      url='http://cheeseshop.python.org/pypi/Interface',
      license='ZPL 2.1',
      description='Interface implementation',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description="""\
This package provides an interface implementation for Python as it was
used in Zope 2.  Unless you need it for legacy Zope 2 applications,
you probably want to use the more modern zope.interface package.""",

      packages=find_packages('src'),
      package_dir={'': 'src'},

      install_requires=['zope.interface', 'zope.schema'],
      include_package_data=True,
      zip_safe=False,
      )
