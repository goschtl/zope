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
"""Setup for z3hello package

$Id$
"""

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'z3hello',
      version = '0.2',
      url = 'http://svn.zope.org/Sandbox/baijum/z3hello/trunk',
      license = 'ZPL 2.1',
      description = 'A Zope 3 hello app solely from eggs using zc.buildout',
      author = 'Zope Corporation and Contributors',
      author_email = 'zope3-dev@zope.org',
      long_description=(
        read('README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        ),
 
      packages = find_packages('src'),
      package_dir = {'': 'src'},

      tests_require = ['zope.testing'],
      install_requires = ['setuptools',
                          'zope.app.zcmlfiles',
                          'zope.app.twisted',
                          'zope.app.securitypolicy',
                         ],

      include_package_data = True,
      zip_safe = False,
      entry_points = """
      [paste.app_factory]
      main = z3hello.startup:application_factory
      """
      )
