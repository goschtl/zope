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
"""Setup for z3ext.controlpanel package

$Id$
"""
import sys, os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version='0'


setup(name = 'z3ext.controlpanel',
      version = version,
      description = "Control Panel - userfriendly system control panel.",
      long_description = (
        'Detailed Documentation\n' +
        '======================\n'
        + '\n\n' +
        read('src', 'z3ext', 'controlpanel', 'README.txt')
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
      author = 'Nikolay Kim',
      author_email = 'fafhrd91@gmail.com',
      url='http://pypi.python.org/pypi/z3ext.controlpanel/',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'':'src'},
      namespace_packages=['z3ext'],
      install_requires = ['setuptools', 'ZODB3',
                          'zope.schema',
                          'zope.interface',
                          'zope.component',
                          'zope.annotation',
                          'zope.security',
                          'zope.location',
                          'zope.publisher',
                          'zope.i18n',
                          'zope.i18nmessageid',
                          'zope.viewlet',
                          'zope.contentprovider',
                          'zope.cachedescriptors',
                          'zope.lifecycleevent',
                          'zope.configuration',
                          'zope.site',
                          'zope.container',
                          'z3c.traverser',
                          'z3ext.layout',
                          'z3ext.layoutform',
                          'z3ext.resourcepackage',
                          ],
      extras_require = dict(test=[
          'z3c.breadcrumb',
          'z3ext.autoinclude',
          'z3ext.security',
          'z3ext.ui.breadcrumbs',
          'z3ext.wizard',
          'zope.app.folder',
          'zope.app.testing',
          'zope.dublincore >= 3.7',
          'zope.login',
          'zope.principalregistry',
          'zope.securitypolicy',
          'zope.testbrowser',
          'zope.testing',
          ]),
      include_package_data = True,
      zip_safe = False
      )
