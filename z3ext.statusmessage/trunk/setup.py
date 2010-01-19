##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Setup for z3ext.statusmessage package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0'


setup(name='z3ext.statusmessage',
      version=version,
      description="Status messages",
      long_description=(
          'Detailed Dcoumentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'z3ext', 'statusmessage', 'README.txt')
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
      url='http://pypi.python.org/pypi/z3ext.statusmessage/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['z3ext'],
      install_requires = ['setuptools',
                          'zope.component',
                          'zope.interface',
                          'zope.session',
                          'zope.publisher',
                          'zope.contentprovider',
                          'z3ext.cacheheaders',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.testbrowser',
                                  'zope.browserpage',
                                  'zope.browserresource',
                                  'zope.principalregistry',
                                  'zope.securitypolicy',
                                  'zope.contentprovider',
                                  'z3ext.autoinclude',
                                  ]),
      include_package_data = True,
      zip_safe = False
      )
