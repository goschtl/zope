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
"""Setup for z3ext.preferences package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name = 'z3ext.preferences',
      version = version,
      author = 'Nikolay Kim',
      author_email = 'fafhrd91@gmail.com',
      description = "z3ext principal preferences",
      long_description = (
        'Detailed Documentation\n' +
        '======================\n'
        + '\n\n' +
        read('src', 'z3ext', 'preferences', 'tests', 'README.txt')
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
      url='http://pypi.python.org/pypi/z3ext.preferences/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['z3ext'],
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.component',
                          'zope.interface',
                          'zope.annotation',
                          'zope.publisher',
                          'zope.configuration',
                          'zope.schema',
                          'zope.location',
                          'zope.security',
                          'zope.securitypolicy',
                          'zope.cachedescriptors',
                          'zope.pagetemplate',
                          'zope.i18n',
                          'zope.i18nmessageid',
                          'zope.viewlet',
                          'zope.contentprovider',
                          'zope.site',
                          'zope.authentication',
                          'zope.principalannotation',
                          'zope.processlifetime',
                          'zope.app.appsetup',
                          'z3c.traverser',
                          'z3ext.layout',
                          'z3ext.layoutform',
                          'z3ext.statusmessage',
                          'z3ext.resourcepackage',
                          ],
      extras_require = dict(test=[
          'z3c.breadcrumb',
          'z3ext.authentication',
          'z3ext.autoinclude',
          'z3ext.ui.breadcrumbs',
          'zope.app.generations',
          'zope.app.testing',
          'zope.login',
          'zope.principalregistry',
          'zope.testbrowser',
          'zope.testing',
          ]),
      include_package_data = True,
      zip_safe = False
      )
