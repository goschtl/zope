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
"""Setup for lovely.relation package

$Id$
"""

import os

from setuptools import setup, find_packages, Extension

setup(name='lovely.relation',
      version='1.0.0',
      url='http://svn.zope.org/lovely.relation',
      license='ZPL 2.1',
      description='Lovely Relation Packages for Zope3',
      author='Lovely Systems',
      author_email='office@lovelysystems.com',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['lovely',],
      extras_require=dict(test=['zope.app.testing',
                                'zope.app.intid',
                                'z3c.testing',
                                'zope.testbrowser',
                                'zope.app.zcmlfiles',
                                'zope.app.securitypolicy',
                                ]),
      install_requires=['setuptools',
                        'ZODB3',
                        'z3c.configurator',
                        'zc.relationship <= 1.999',
                        'zope.app.container',
                        'zope.i18nmessageid',
                        'zope.index', # needed by zc.relationship, but
                                      # no dep
                        'zope.schema',
                        'zope.security',
                        ],
      include_package_data = True,
      zip_safe = False,
      )
