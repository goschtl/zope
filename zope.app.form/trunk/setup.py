##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Setup for zope.app.form package

$Id: setup.py 81002 2007-10-24 01:19:47Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.form',
      version = '4.0.3dev',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='The Original Zope 3 Form Framework',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed documentation:\n'
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 form widget zcml",
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3'],
      url='http://pypi.python.org/pypi/zope.app.form',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require={'test': [
            'ZODB3',
            'zc.sourcefactory',
            'zope.container',
            'zope.principalregistry',
            'zope.site',
            'zope.traversing',
            'zope.app.appsetup',
            'zope.app.publication',
            'zope.app.testing',
            ]},
      install_requires=[
          "setuptools",
          "transaction",
          "zope.formlib >= 4.0",
          "zope.browser>=1.1",
          "zope.browserpage>=3.10.1",
          "zope.browsermenu",
          "zope.component",
          "zope.configuration",
          "zope.datetime",
          "zope.exceptions",
          "zope.i18n",
          "zope.interface",
          "zope.proxy",
          "zope.publisher",
          "zope.schema>=3.5.1dev",
          "zope.security",
          ],
      include_package_data = True,
      zip_safe = False,
      )

