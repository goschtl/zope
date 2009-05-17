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
"""Setup for zope.location package
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    text = open(os.path.join(os.path.dirname(__file__), *rnames)).read()
    return text

setup(name='zope.location',
      version = '3.5.4',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Zope Location',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '======================'
          + '\n\n' +
          read('src', 'zope', 'location', 'location.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      license='ZPL 2.1',
      keywords=('zope3 location strutural'),
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
      url='http://pypi.python.org/pypi/zope.location/',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope',],
      install_requires=['setuptools',
                        'zope.interface',
                        'zope.schema>=3.5.1dev',
                        'zope.component',
                        'zope.proxy>3.3',
                        'zope.copy',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
