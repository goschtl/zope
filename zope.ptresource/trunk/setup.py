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
"""zope.ptresource setup
"""
from setuptools import setup, find_packages

long_description = (open('README.txt').read() + '\n\n' +
                    open('CHANGES.txt').read())

setup(name='zope.ptresource',
      version = '4.0.0dev',
      url='http://pypi.python.org/pypi/zope.ptresource/',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      classifiers = ['Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Zope Public License',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2',
                     'Programming Language :: Python :: 2.6',
                     'Programming Language :: Python :: 2.7',
                     'Operating System :: OS Independent',
                     'Topic :: Internet :: WWW/HTTP',
                     'Framework :: Zope3',
                     ],
      description='Page template resource plugin for zope.browserresource',
      long_description=long_description,
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},

      namespace_packages=['zope'],
      include_package_data=True,
      install_requires=['setuptools',
                        'zope.browserresource',
                        'zope.interface',
                        'zope.pagetemplate',
                        'zope.publisher',
                        'zope.security[untrustedpython]',
                        ],
      extras_require={
          'test': ['zope.testing'],
          },

      zip_safe = False,
      )
