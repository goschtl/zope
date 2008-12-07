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
"""Setup for ``zope.kgs`` project"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.kgs',
      version = '0.2.0',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='Known-Good-Set (KGS) Support',
      long_description=(
          read('README.txt')
          + '\n\n' +
          read('src', 'zope', 'kgs', 'README.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 setuptools egg kgs",
      classifiers = [
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://cheeseshop.python.org/pypi/zope.kgs',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      extras_require = dict(
          test=['zope.testing'],
          ),
      install_requires=[
          'lxml',
          'setuptools',
          'zc.buildout',
          'zope.pagetemplate',
          ],
      entry_points = dict(console_scripts=[
          'generate-buildout = zope.kgs.buildout:main',
          'generate-versions = zope.kgs.version:main',
          'generate-index = zope.kgs.ppix:main',
          'generate-links = zope.kgs.link:main',
          'generate-intro = zope.kgs.intro:main',
          'generate-site = zope.kgs.site:main',
          'list-latest = zope.kgs.latest:main',
          'list-changes = zope.kgs.change:main',
          ]),
      include_package_data = True,
      zip_safe = False,
      )
