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
"""Setup for zope.server package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name='zope.server',
      version = '3.5.0a3',
      url='http://svn.zope.org/zope.server',
      license='ZPL 2.1',
      description='Zope server',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description=open('README.txt').read(),

      packages=find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages=['zope',],

      tests_require = ['zope.testing',
                       'zope.i18n',
                       'zope.component'],
      install_requires = ['setuptools',
                          'zope.interface',
                          'zope.publisher',
                          'zope.security',
                          'zope.deprecation',
                          'ZODB3'],
      include_package_data = True,
      zip_safe = False,
      entry_points = """
      [paste.server_runner]
      main = zope.server.http.wsgihttpserver:run_paste
      """
      )
