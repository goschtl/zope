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
"""Psycopg Database Adapter for Zope 3

This package allows Zope 3 to connect to any PostGreSQL database via
the common Zope 3 RDB connection facilities.

$Id: setup.py 83394 2008-02-01 19:51:10Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.psycopgda',
      version = '1.2.0dev',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Psycopg Database Adapter for Zope 3',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 rdn postgresql psycopg",
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
      url='http://pypi.python.org/pypi/zope.psycopgda',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require = dict(
          test=['zope.testing',
                ]),
      install_requires = [
          # Versions 1.x is not a proper egg.
          #'psycopgda',
          'setuptools',
          'zope.component',
          'zope.interface',
          'zope.rdb',
          'zope.app.form',
          ],
      include_package_data = True,
      zip_safe = False,
      )
