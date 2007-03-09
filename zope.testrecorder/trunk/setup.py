##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Setup for zope.testrecorder package

$Id$
"""
try:
    from setuptools import setup, Extension
except ImportError, e:
    from distutils.core import setup, Extension

setup(name='zope.testrecorder',
      version='3.4dev',

      url='http://svn.zope.org/zope.testrecorder',
      license='ZPL 2.1',
      description='Test recorder for functional tests',
      author='Zope Corporation and Contributors',
      author_email='zope3-dev@zope.org',
      long_description="""\
The testrecorder is a browser-based tool to support the rapid
development of functional tests for Web-based systems and
applications.  The idea is to "record" tests by exercising whatever is
to be tested within the browser.  The test recorder will turn a
recorded session into a functional test.""",
      keywords='web testing',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: Zope Public License',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP :: Browsers',
          'Topic :: Software Development :: Testing',
          ],

      packages=['zope', 'zope.testrecorder'],
      package_dir = {'': 'src'},
      namespace_packages=['zope'],
      package_data = {
          '': ['*.txt', '*.zcml'],
          'zope.testrecorder': ['www/*', 'html/*'],
          },

      zip_safe = False,
      )
