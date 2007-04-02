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
"""Setup for zwiki package

$Id: setup.py 73414 2007-03-21 09:21:03Z baijum $
"""

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'zwiki',
      version = '0.3dev',
      url = 'http://svn.zope.org/zwiki/trunk',
      license = 'ZPL 2.1',
      description = 'A Zope 3 wiki',
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
                          'zope.schema',
                          'zope.sendmail',
                          'zope.app.zcmlfiles',
                          'zope.app.twisted',
                          'zope.app.securitypolicy',
                          'zope.app.layers',
                          'zope.app.zptpage',
                          'zope.app.skins',
                          'zope.app.renderer',
                          ],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testbrowser',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles']),

      include_package_data = True,
      zip_safe = False,
      )
