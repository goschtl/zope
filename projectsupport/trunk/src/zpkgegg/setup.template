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
"""Setup for %(Name)s package

$Id$
"""

import os


try:
    from setuptools import setup, Extension, find_packages
    pkg_list = find_packages(os.path.join(os.path.dirname(__file__), 'src'))
except ImportError, e:
    from distutils.core import setup, Extension
    pkg_list = ['zope', '%(Name)s']

setup(name='%(Name)s',
      version='%(version)s',

      url='%(Home-page)s',
      license='%(License)s',
      description='%(Summary)s',
      author='%(Author)s',
      author_email='%(Author-email)s',
      long_description='%(Description)s',

      packages=pkg_list,
      package_dir = {'': os.path.join(os.path.dirname(__file__), 'src')},

      ext_modules=[%(extensions)s],

      namespace_packages=['zope',],
      tests_require = ['zope.testing'],
      install_requires=%(dependencies)s,
      include_package_data = True,

      zip_safe = False,
      )
