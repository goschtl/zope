###############################################################################
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
"""Setup for z3c.traverser package

$Id: setup.py 81038 2007-10-24 14:34:17Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='z3c.traverser',
      version = '0.2.5',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='Pluggable Traversers And URL handling utilities',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'z3c', 'traverser', 'README.txt')
          + '\n\n' +
          read('src', 'z3c', 'traverser', 'namespace.txt')
          + '\n\n' +
          read('src', 'z3c', 'traverser', 'viewlet', 'README.txt')
          + '\n\n' +
          read('src', 'z3c', 'traverser', 'viewlet', 'BROWSER.txt')
          + '\n\n' +
          read('src', 'z3c', 'traverser', 'stackinfo', 'README.txt')
          + '\n\n' +
          read('src', 'z3c', 'traverser', 'stackinfo', 'BROWSER.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 traverser pluggable plugin viewlet",
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
      url='http://pypi.python.org/pypi/z3c.traverser',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require = dict(
          test = ('zope.app.testing',
                  'zope.app.securitypolicy',
                  'zope.app.zcmlfiles',
                  'zope.testbrowser'),
          ),
      install_requires=(
          'setuptools',
          'zope.component',
          'zope.contentprovider',
          'zope.interface',
          'zope.publisher',
          'zope.traversing',
          'zope.viewlet',
          ),
      include_package_data = True,
      zip_safe = False,
      )
