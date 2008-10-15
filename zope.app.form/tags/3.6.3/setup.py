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
"""Setup for zope.app.form package

$Id: setup.py 81002 2007-10-24 01:19:47Z srichter $
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.form',
      version = '3.6.3',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='The Original Zope 3 Form Framework',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed documentation:\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'form', 'browser', 'README.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'form', 'browser', 'widgets.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'form', 'browser', 'objectwidget.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'form', 'browser', 'source.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'form', 'browser', 'i18n.txt')
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
      url='http://cheeseshop.python.org/pypi/zope.app.form',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require={"test": ['zope.app.testing',
                               'zope.app.securitypolicy',
                               'zc.sourcefactory',
                               'zope.app.zcmlfiles']},
      install_requires=[
          "setuptools",
          "ZODB3",
          "zope.app.container",
          "zope.app.publisher",
          "zope.cachedescriptors",
          "zope.component",
          "zope.configuration",
          "zope.deprecation",
          "zope.exceptions",
          "zope.i18n",
          "zope.interface",
          "zope.proxy",
          "zope.publisher",
          "zope.schema",
          "zope.security",
          "zope.app.basicskin",
          "zope.location",
          ],
      include_package_data = True,
      zip_safe = False,
      )

