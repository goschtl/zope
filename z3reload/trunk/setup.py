##############################################################################
#
# Copyright (c) 2006--2008 Zope Corporation and Contributors.
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
"""Setup for z3reload package
"""
from setuptools import find_packages
from setuptools import setup

long_description = (open('README.txt').read() +
                    '\n\n' +
                    open('CHANGES.txt').read())


setup(name='z3reload',
      version='0.1dev',
      license='ZPL 2.1',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description="Enables automatic reloading of Zope3 view code.",
      long_description=long_description,

      packages=find_packages('src'),
      package_dir={'': 'src'},
      tests_require=['zope.testing'],
      install_requires=['setuptools',
                        'zope.app.pagetemplate',
                        'zope.app.publisher',
                        'zope.component',
                        'zope.configuration',
                        'zope.publisher',
                       ],
      extras_require=dict(
          test=[
              'zope.app.testing',
              'zope.app.zcmlfiles',
              ]),
      include_package_data=True,
      zip_safe=False,
      )
