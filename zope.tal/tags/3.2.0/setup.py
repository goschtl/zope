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
"""Setup for zope.tal package

$Id$
"""

import os

try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.tal',
      version='3.2.0.1',
      url='http://svn.zope.org/zope.tal/tags/3.2.0',
      license='ZPL 2.1',
      description='Zope3 Template Application Languate (TAL)',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      
      packages=['zope',
                'zope.tal',
               ],
      package_dir = {'': os.path.join(os.path.dirname(__file__), 'src')},

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=['zope.deprecation',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.interface',
                       ],
      include_package_data = True,

      zip_safe = False,
      )
