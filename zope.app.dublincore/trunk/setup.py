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
"""Setup for zope.app.dublincore package

$Id$
"""
from setuptools import setup, find_packages

setup(name='zope.app.dublincore',
      version = '3.4.0dev',
      url='http://pypi.python.org/pypi/zope.app.dublincore',
      license='ZPL 2.1',
      description='''A deprecated backwards compatibility package
                     which will go away in 3.5''',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope', 'zope.app'],
      install_requires=['setuptools',
                        'zope.dublincore',
                        'zope.deprecation',
                       ],
      include_package_data = True,
      zip_safe = False,
      )
