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
"""Setup for zope.fssync package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name='zope.fssync',
      version = '3.4.0a1',
      url='http://svn.zope.org/zope.fssync',
      license='ZPL 2.1',
      description='Zope fssync',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="Filesystem synchronization utility for Zope 3.",

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.proxy',
                        'zope.xmlpickle'],
      include_package_data = True,

      zip_safe = False,
      )
