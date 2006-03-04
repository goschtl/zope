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
"""Zope Object Database: object database and persistence

The Zope Object Database provides an object-oriented database for
Python that provides a high-degree of transparency. Applications can
take advantage of object database features with few, if any, changes
to application logic.  ZODB includes features such as a plugable storage
interface, rich transaction support, and undo.

This distribution includes the TimeStamp module from ZODB.
"""

# The (non-obvious!) choices for the Trove Development Status line:
# Development Status :: 5 - Production/Stable
# Development Status :: 4 - Beta
# Development Status :: 3 - Alpha

import os
from setuptools import setup, Extension

classifiers = """\
Development Status :: 5 - Production
Intended Audience :: Developers
License :: OSI Approved :: Zope Public License
Programming Language :: Python
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Microsoft :: Windows
Operating System :: Unix
"""

timestamp = Extension(name = 'zope.timestamp',
                      include_dirs = ['src/zope'],
                      sources= ['src/zope/TimeStamp.c']
                      )

setup(name='zope.timestamp',
      version='3.6.0',
      url='http://svn.zope.org/ZODB',
      download_url = "http://www.zope.org/Products/ZODB3.6",
      license='ZPL 2.1',
      description='ZODB TimeStamp implementation',
      author='Zope Corporation and Contributors',
      maintainer='Zope Corporation and Contributors',
      author_email='zodb-dev@zope.org',
      maintainer_email='zodb-dev@zope.org',
      platforms = ['any'],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = __doc__,
      packages=['zope'],
      package_dir = {'': 'src'},
      ext_modules=[timestamp],
      tests_require = [],
      install_requires=[],
      include_package_data = True,
      zip_safe = True,
      )


