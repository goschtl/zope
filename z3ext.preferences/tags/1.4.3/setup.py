##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

version='1.4.3'


setup(name = 'z3ext.preferences',
      version = version,
      author = 'Nikolay Kim',
      author_email = 'fafhrd91@gmail.com',
      description = "z3ext principal preferences",
      long_description = (
        'Detailed Documentation\n' +
        '======================\n'
        + '\n\n' +
        read('src', 'z3ext', 'preferences', 'README.txt')
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
      url='http://z3ext.net/',
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
			  'zope.app.security',
                          'zope.app.component',
			  'zope.app.publisher',
			  'zope.app.pagetemplate',
			  'zope.app.principalannotation',
                          'z3c.traverser',
			  'z3c.autoinclude',
			  'z3ext.layout >= 1.5.1',
			  'z3ext.layoutform >= 1.2.3',
                          'z3ext.statusmessage',
			  'z3ext.resourcepackage',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  ]),
      include_package_data = True,
      zip_safe = False
      )
