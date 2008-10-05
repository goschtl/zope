##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Setup for z3ext.resource package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.0'


setup(name='z3ext.resource',
      version=version,
      description="Extended resource",
      long_description=(
          'Detailed Dcoumentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'z3ext', 'resource', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Framework :: Zope3'],
      author='Nikolay Kim',
      author_email='fafhrd91@gmail.com',
      url='http://z3ext.net/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['z3ext'],
      install_requires = ['setuptools',
                          'zope.schema',
                          'zope.component',
                          'zope.interface',
			  'zope.configuration',
			  'zope.publisher',
			  'zope.security',
                          'zope.app.publisher',
                          'z3c.autoinclude',
                          'z3c.zrtresource>=1.1.0',
			  'z3ext.cacheheaders',
                          ],
      extras_require = dict(test=['zope.traversing',
                                  'zope.app.testing',
                                  'zope.testing',
                                  'zope.testbrowser',
                                  ]),
      include_package_data = True,
      zip_safe = False
      )
