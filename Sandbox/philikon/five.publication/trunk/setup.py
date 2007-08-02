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
"""Setup for the five.publisher package
"""
import os
from setuptools import setup, find_packages

setup(name='five.publication',
      version = '0.1',
      url='http://cheeseshop.python.org/pypi/five.publication',
      license='ZPL 2.1',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      description="Run Zope 2 web applications on the WSGI-enabled object "
                  "object publishing framework of zope.publisher",
      long_description="",

      packages=find_packages(),

      install_requires=['setuptools',
                        'Zope2',
                        'ZODB3', # for the transaction package
                        'zope.publisher',
                        'zope.event',
                        'zope.interface',
                        'zope.component',
                        'zope.traversing',
                        'zope.security',
                        'zope.app.publication',
                        ],
      include_package_data=True,
      zip_safe=False,
      entry_points = """
      [paste.app_factory]
      demo = five.publicationdemo.application:application_factory
      """
      )
