##############################################################################
#
# Copyright (c) 2007-2009 Zope Corporation and Contributors.
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
"""Setup for z3c.viewlet package

$Id: setup.py 81038 2007-10-24 14:34:17Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.1.0'

setup(name='z3c.viewlet',
      version = version,
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='DEPRCATED: Collection of Viewlet Extensions',
      long_description=read('README.txt'),
      keywords = "zope3 viewlet extension weight ordered",
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
      url='http://pypi.python.org/pypi/z3c.viewlet',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['z3c'],
      extras_require=dict(test=['zope.testing']),
      install_requires=['setuptools',
                        'zope.viewlet',
                        'zope.deferredimport',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
