##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Setup for z3ext.formatter package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0'


setup(name='z3ext.formatter',
      version=version,
      description="Extensible TALES fomratter expression.",
      long_description=(
          'Detailed Dcoumentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'z3ext', 'formatter', 'README.txt')
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
      url='http://pypi.python.org/pypi/z3ext.formatter/',
      license='ZPL 2.1',
      package_dir = {'':'src'},
      packages=find_packages('src'),
      namespace_packages=['z3ext'],
      install_requires = ['setuptools', 'pytz',
                          'zope.component',
                          'zope.interface',
                          'zope.publisher',
                          'zope.schema',
                          'zope.proxy',
                          'zope.tales',
                          'zope.i18n',
                          'zope.i18nmessageid',
                          'z3c.pt',
                          'z3ext.layout',
                          'z3ext.controlpanel',
                          'z3ext.resourcepackage',
                          'z3ext.jquery.i18n',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'z3ext.autoinclude',
                                  'z3ext.controlpanel [test]',
                                  ]),
      include_package_data = True,
      zip_safe = False
      )
