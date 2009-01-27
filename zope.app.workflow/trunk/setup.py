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
"""Setup for zope.app.workflow package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.workflow',
      version = '3.5dev',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Workflow Engine for Zope 3',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 workflow wfmc",
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
      url='http://cheeseshop.python.org/pypi/zope.app.workflow',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require=dict(test=['zope.app.testing',
                                'zope.app.zcmlfiles',
                                'zope.app.file',
                                'zope.app.securitypolicy']),
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.component',
                          'zope.interface',
                          'zope.lifecycleevent',
                          'zope.app.container',
                          'zope.tales',
                          'zope.security',
                          'zope.schema',
                          'zope.security',
                          'zope.proxy',
                          'zope.traversing',
                          'zope.event',
                          'zope.app.i18n',
                          'zope.configuration',
                          'zope.dublincore',
                          'zope.app.pagetemplate',
                          'zope.app.security',
                          'zope.publisher',
                          'zope.app.form'],
      include_package_data = True,
      zip_safe = False,
      )
