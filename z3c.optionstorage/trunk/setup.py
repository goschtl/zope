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
"""Setup for z3c.optionstorage package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='z3c.optionstorage',
      version = '1.0.8dev',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Optional Storages -- Persistent, Managable Vocabularies',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 vocabulary zodb managable",
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
      url='http://pypi.python.org/pypi/z3c.optionstorage',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require=dict(test=['zope.testing']),
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.annotation',
                          'zope.browserpage>=3.10',
                          'zope.component',
                          'zope.configuration',
                          'zope.i18n',
                          'zope.interface',
                          'zope.proxy',
                          'zope.schema',
                          'zope.security',
                          'zope.traversing',
                          'zope.app.form'],
      include_package_data = True,
      zip_safe = False,
      )
