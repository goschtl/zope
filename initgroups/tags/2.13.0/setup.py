##############################################################################
#
# Copyright (c) 2010 Zope Corporation and Contributors.
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

from os.path import join
from setuptools import setup, find_packages, Extension

setup(name='initgroups',
      version = '2.13.0',
      url='http://pypi.python.org/pypi/initgroups',
      license='ZPL 2.1',
      description="Convenience uid/gid helper function used in Zope2.",
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),

      packages=find_packages('src'),
      package_dir={'': 'src'},
      ext_modules=[Extension(
            name='initgroups._initgroups',
            sources=[join('src', 'initgroups', '_initgroups.c')],
            ),
      ],
      include_package_data=True,
      zip_safe=False,
      )
