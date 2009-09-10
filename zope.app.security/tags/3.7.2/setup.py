##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
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

version = '3.7.2'

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name='zope.app.security',
      version = '3.7.2',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description='ZMI Views For Zope3 Security Components',
      long_description=(
          read('README.txt')
          + '\n\n' +
          'Detailed Documentation\n' +
          '======================\n'
          + '\n\n' +
          read('src', 'zope', 'app', 'security', 'browser',
               'authutilitysearchview.txt')
          + '\n\n' +
          read('src', 'zope', 'app', 'security', 'browser', 'loginlogout.txt')
          + '\n\n' +
          read('CHANGES.txt')
          ),
      keywords = "zope security authentication principal ftp http",
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
      url='http://pypi.python.org/pypi/zope.app.security',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zope', 'zope.app'],
      install_requires=['setuptools',
                        'zope.app.form',
                        'zope.app.pagetemplate',
                        'zope.app.publisher',
                        'zope.app.localpermission',
                        'zope.app.testing',
                        'zope.authentication',
                        'zope.component>=3.6.0',
                        'zope.i18n',
                        'zope.i18nmessageid',
                        'zope.interface',
                        'zope.principalregistry',
                        'zope.publisher',
                        'zope.security',
                        'ZODB3',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
