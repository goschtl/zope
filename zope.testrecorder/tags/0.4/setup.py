##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
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
"""Setup for zope.testrecorder package
"""
import os
try:
    from setuptools import setup
except ImportError, e:
    from distutils.core import setup

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.testrecorder',
      version='0.4',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      description='Test recorder for functional tests',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords='web testing',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP :: Browsers',
          'Topic :: Software Development :: Testing',
          ],

      url='http://pypi.python.org/pypi/zope.testrecorder',
      license='ZPL 2.1',
      packages=['zope', 'zope.testrecorder'],
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      install_requires=[
        'setuptools',
      ],
      extras_require={
        'test': ['Zope2']
      },
      include_package_data = True,
      zip_safe = False,
)
