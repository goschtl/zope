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
"""Setup for zope.app.server package

$Id: setup.py 74669 2007-04-23 12:04:26Z ctheune $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.locking',
      version = '3.5.0',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Simple Object Locking Framework for Zope 3 applications',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Dcoumentation\n' +
          '----------------------\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'locking', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 object locking",
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
      url='http://pypi.python.org/pypi/zope.app.locking',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.app.file',
                                  'zope.site', ]),
      install_requires=['setuptools',
                        'zope.security',
                        'zope.app.keyreference',
                        'zope.app.i18n',
                        'zope.interface',
                        'zope.schema',
                        'zope.component',
                        'zope.app.i18n',
                        'ZODB3',
                        'zope.event',
                        'zope.traversing',
                        'zope.size',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
