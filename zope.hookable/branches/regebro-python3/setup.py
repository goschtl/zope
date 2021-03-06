##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
"""Setup for zope.hookable package
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='zope.hookable',
      version = '3.4.2dev',
      url='http://svn.zope.org/zope.hookable',
      license='ZPL 2.1',
      description='Zope hookable',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      long_description="Hookable object support.",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 3.1",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],

      packages=find_packages('src'),
      package_dir={'': 'src'},
      ext_modules=[Extension("zope.hookable._zope_hookable",
                             [os.path.join('src', 'zope', 'hookable',
                                           "_zope_hookable.c")
                              ], extra_compile_args=['-g']),
                   ],
      namespace_packages=['zope',],
      extras_require=dict(test=['zope.testing']),
      install_requires=['setuptools'],
      include_package_data=True,
      zip_safe=False,
      
      test_suite='zope.hookable.tests.test_hookable.test_suite',
      )
