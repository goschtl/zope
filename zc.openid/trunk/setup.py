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

from setuptools import setup, find_packages

setup(name='zc.openid',
      version='0.1',
      description="",
      long_description="",
      keywords='',
      author='',
      author_email='',
      url='',
      license='ZPL 2.1',
      # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Framework :: Zope3',
                   ],

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages = ['zc'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'python-openid',
                        'ZODB3',
                        'zope.app.component',
                        'zope.app.security',
                        'zope.component',
                        'zope.traversing',
                        'zope.interface',
                        'zope.location',
                        'zope.publisher',
                        'zope.session',
                        'zope.security',
                        'zope.formlib',
                        'zope.schema',
                        ],
      extras_require={
          'test': ['zope.app.testing'],
          }
      )
