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

This distribution includes the persistent module from ZODB.
"""

# The (non-obvious!) choices for the Trove Development Status line:
# Development Status :: 5 - Production/Stable
# Development Status :: 4 - Beta
# Development Status :: 3 - Alpha

import os
from setuptools import setup, Extension

classifiers = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: Zope Public License
Programming Language :: Python
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: Microsoft :: Windows
Operating System :: Unix
"""

cPersistence = Extension(name = 'persistent.cPersistence',
                         include_dirs = ['src'],
                         sources= ['src/cPersistence.c',
                                   'src/ring.c'],
                         depends = ['src/cPersistence.h',
                                    'src/ring.h',
                                    'src/ring.c']
                         )

cPickleCache = Extension(name = 'persistent.cPickleCache',
                         include_dirs = ['src'],
                         sources= ['src/cPickleCache.c',
                                   'src/ring.c'],
                         depends = ['src/cPersistence.h',
                                    'src/ring.h',
                                    'src/ring.c']
                         )

TimeStamp = Extension(name = 'persistent.TimeStamp',
                      include_dirs = ['src'],
                      sources= ['src/TimeStamp.c']
                      )

setup(name='persistent',
      version='3.6.0',
      url='http://svn.zope.org/ZODB',
      download_url = "http://www.zope.org/Products/ZODB3.6",
      license='ZPL 2.1',
      description='ZODB persistence implementation',
      author='Zope Corporation and Contributors',
      maintainer='Zope Corporation and Contributors',
      author_email='zodb-dev@zope.org',
      maintainer_email='zodb-dev@zope.org',
      headers = ['src/cPersistence.h'],
      platforms = ['any'],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = __doc__,
      packages=['persistent', 'persistent.tests'],
      package_dir = {'persistent': 'src'},
      ext_modules=[cPersistence, cPickleCache, TimeStamp],
      tests_require = [],
      install_requires=[],
      include_package_data = True,
      zip_safe = True,
      )


