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
"""Setup for zope.container package

$Id$
"""
import os
from setuptools import setup, find_packages, Extension

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.container',
      version = '3.6.0',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Zope Container',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n'
          '**********************\n'
          + '\n\n' +
          read('src', 'zope', 'container', 'constraints.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 container",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://cheeseshop.python.org/pypi/zope.container',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', ],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.component',
                        'zope.size',
                        'zope.dottedname',
                        'zope.location',
                        'zope.lifecycleevent',
                        'zope.deprecation',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
