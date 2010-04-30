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
"""zope.browsermenu setup
"""
from setuptools import setup, find_packages

long_description = (open('README.txt').read() + '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.browsermenu',
      version = '3.9.1',
      url='http://pypi.python.org/pypi/zope.browsermenu/',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      classifiers = ['Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Zope Public License',
                     'Programming Language :: Python',
                     'Operating System :: OS Independent',
                     'Topic :: Internet :: WWW/HTTP',
                     'Framework :: Zope3',
                     ],
      description='Browser menu implementation for Zope.',
      long_description=long_description,

      packages=find_packages('src'),
      package_dir={'': 'src'},

      namespace_packages=['zope'],
      include_package_data=True,
      install_requires=['setuptools',
                        'zope.browser',
                        'zope.component>=3.7',
                        'zope.configuration',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.pagetemplate>=3.5',
                        'zope.publisher',
                        'zope.schema',
                        'zope.security[untrustedpython]',
                        'zope.traversing>3.7',
                        ],
      extras_require={
          'test': ['zope.testing'],
          },

      zip_safe = False,
      )
