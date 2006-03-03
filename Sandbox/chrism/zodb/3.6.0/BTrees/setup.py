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

This distribution includes the BTrees (B+ Tree) implementation for ZODB.
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

# Set up dependencies for the BTrees package
base_btrees_depends = [
    "src/BTreeItemsTemplate.c",
    "src/BTreeModuleTemplate.c",
    "src/BTreeTemplate.c",
    "src/BucketTemplate.c",
    "src/MergeTemplate.c",
    "src/SetOpTemplate.c",
    "src/SetTemplate.c",
    "src/TreeSetTemplate.c",
    "src/sorters.c",
    "src/cPersistence.h",
    ]

_flavors = {"O": "object", "I": "int", "F": "float"}

KEY_H = "src/%skeymacros.h"
VALUE_H = "src/%svaluemacros.h"

def BTreeExtension(flavor):
    key = flavor[0]
    value = flavor[1]
    name = "BTrees._%sBTree" % flavor
    sources = ["src/_%sBTree.c" % flavor]
    kwargs = {"include_dirs": ['src']}
    if flavor != "fs":
        kwargs["depends"] = (base_btrees_depends + [KEY_H % _flavors[key],
                                                    VALUE_H % _flavors[value]])
    if key != "O":
        kwargs["define_macros"] = [('EXCLUDE_INTSET_SUPPORT', None)]
    return Extension(name, sources, **kwargs)

setup(name='BTrees',
      version='3.6.0',
      url='http://svn.zope.org/ZODB',
      download_url = "http://www.zope.org/Products/ZODB3.6",
      license='ZPL 2.1',
      description='ZODB BTrees implementation',
      author='Zope Corporation and Contributors',
      maintainer='Zope Corporation and Contributors',
      author_email='zodb-dev@zope.org',
      maintainer_email='zodb-dev@zope.org',
      headers = ['src/cPersistence.h'],
      platforms = ['any'],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = __doc__,
      packages=['BTrees',],
      package_dir = {'BTrees': 'src'},
      ext_modules=[BTreeExtension(flavor) for flavor in
                   ("OO", "IO", "OI", "II", "IF", "fs")],
      tests_require = [],
      install_requires=[],
      include_package_data = True,
      zip_safe = True,
      )

