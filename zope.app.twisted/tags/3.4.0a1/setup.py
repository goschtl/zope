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
"""Setup for zope.app.twisted package

$Id$
"""

import os

from setuptools import setup, find_packages

setup(name = 'zope.app.twisted',
      version = '3.4dev',
      url = 'http://svn.zope.org/zope.app.twisted',
      license = 'ZPL 2.1',
      description = 'Zope app.twisted',
      author = 'Zope Corporation and Contributors',
      author_email = 'zope3-dev@zope.org',
      long_description = "",

      packages = find_packages('src'),
      package_dir = {'': 'src'},

      namespace_packages = ['zope', 'zope.app'],
      install_requires = ['setuptools',
                          'ZConfig',
                          'ZODB3',
                          'zdaemon',
                          'zope.copypastemove',
                          'zope.event',
                          'zope.exceptions',
                          'zope.interface',
                          'zope.publisher',
                          'zope.security',
                          'zope.app.applicationcontrol',
                          'zope.app.appsetup',
                          'zope.app.publication',
                          'zope.app.wsgi',
                          'zope.app.server',
                          'zope.app.zapi',
                          ],
      extras_require = dict(test=['zope.app.testing',]),
      include_package_data = True,

      zip_safe = False,
      )
