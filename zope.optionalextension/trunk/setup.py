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
# This package is developed by the Zope Toolkit project, documented here:
# http://docs.zope.org/zopetoolkit
# When developing and releasing this package, please follow the documented
# Zope Toolkit policies as described by this documentation.
##############################################################################
""" Setup for zope.optionalextension package
"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
    extras = {}
else:
    extras = {'test_suite': 'zope.optionalextension.tests',
             }

README = open('README.txt').read()
CHANGES = open('CHANGES.txt').read()

setup(name='zope.optionalextension',
      version = '1.0',
      url='http://pypi.python.org/pypi/zope.optionalextension',
      license='ZPL 2.1',
      description='Optional compilation of C extensions',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      long_description='\n\n'.join([README, CHANGES]),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      packages = ['zope', 'zope.optionalextension'],
      package_dir = {'': 'src'},
      **extras
)
