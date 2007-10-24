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
"""Setup for zope.app.i18nfile package

$Id$
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'zope.app.i18nfile',
      version = '3.5.0',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      description='I18n File and Image -- Zope 3 Content Components',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Dcoumentation\n' +
          '----------------------\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'i18nfile', 'browser', 'i18nfile.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'i18nfile', 'browser', 'i18nimage.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope3 i18n l10n file image content",
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
      url='http://cheeseshop.python.org/pypi/zope.app.i18nfile',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles']),
      install_requires = ['setuptools',
                          'ZODB3',
                          'zope.app.file',
                          'zope.i18n',
                          'zope.interface',
                          'zope.size',
                          ],
      include_package_data = True,
      zip_safe = False,
      )
