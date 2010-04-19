#!python
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
"""Setup

$Id: setup.py 313 2007-05-22 15:33:41Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'z3c.layer',
      version = '0.2.5',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='RETIRED: Collection of Alternative Base Layers',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 layer",
      classifiers = [
          'Development Status :: 7 - Inactive',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://cheeseshop.python.org/pypi/z3c.layer',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require = dict(
          test=['zope.app.testing',
                'zope.securitypolicy',
                'zope.app.securitypolicy',
                'zope.testbrowser',
                ]
          ),
      install_requires = [
          'setuptools',
          'z3c.pagelet',
          'zope.app.http',
          'zope.app.form',
          'zope.app.publisher',
          'zope.configuration',
          'zope.traversing',
          ],
      include_package_data = True,
      zip_safe = False,
      )
