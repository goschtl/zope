##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

setup(name='zExceptions',
      version = '2.13.0',
      url='http://pypi.python.org/pypi/zExceptions',
      license='ZPL 2.1',
      description="zExceptions contains common exceptions used in Zope2.",
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      long_description=open('README.txt').read() + '\n' +
                       open('CHANGES.txt').read(),

      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=[
        'setuptools',
        'zope.interface',
        'zope.publisher',
        'zope.security',
      ],
      include_package_data=True,
      zip_safe=False,
      )
