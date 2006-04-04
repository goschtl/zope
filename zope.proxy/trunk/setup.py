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
"""Setup for zope.proxy package

$Id$
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.proxy',
      version='1.0',
      url='http://svn.zope.org/zope.proxy',
      license='ZPL 2.1',
      description='Zope Proxies',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description='',
      
      packages=['zope', 'zope.proxy'],
      package_dir = {'': os.path.join(os.path.dirname(__file__), 'src')},

       ext_modules=[Extension("zope.proxy._zope_proxy_proxy",
                              [os.path.join('src', 'zope', 'proxy',
                                            "_zope_proxy_proxy.c")
                               ]),
                    ],

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['zope.deprecation'],
      include_package_data = True,

      zip_safe = False,
      )
