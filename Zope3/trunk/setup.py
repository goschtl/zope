##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

"""Zope application server, version 3

Zope is a leading open source application server, specializing in content
management, portals, and custom applications.  Zope enables teams to
collaborate in the creation and management of dynamic web-based business
applications such as intranets and portals.
"""

import os
import sys
import glob

from distutils.core import setup
from distutils.extension import Extension

# A hack to determine if Extension objects support the depends keyword arg,
# which only exists in Python 2.3's distutils.
if not "depends" in Extension.__init__.func_code.co_varnames:
    # If it doesn't, create a local replacement that removes depends from the
    # kwargs before calling the regular constructor.
    _Extension = Extension
    class Extension(_Extension):
        def __init__(self, name, sources, **kwargs):
            if "depends" in kwargs:
                del kwargs["depends"]
            _Extension.__init__(self, name, sources, **kwargs)

base_btrees_depends = [
    "lib/python/Persistence/cPersistence.h",
    "lib/python/Persistence/cPersistenceAPI.h",
    "lib/python/Persistence/BTrees/BTreeItemsTemplate.c",
    "lib/python/Persistence/BTrees/BTreeModuleTemplate.c",
    "lib/python/Persistence/BTrees/BTreeTemplate.c",
    "lib/python/Persistence/BTrees/BucketTemplate.c",
    "lib/python/Persistence/BTrees/MergeTemplate.c",
    "lib/python/Persistence/BTrees/SetOpTemplate.c",
    "lib/python/Persistence/BTrees/SetTemplate.c",
    "lib/python/Persistence/BTrees/TreeSetTemplate.c",
    "lib/python/Persistence/BTrees/sorters.c",
    ]

_flavors = {"O": "object", "I": "int"}

KEY_H = "lib/python/Persistence/BTrees/%skeymacros.h"
VALUE_H = "lib/python/Persistence/BTrees/%svaluemacros.h"

def BTreeExtension(flavor):
    key = flavor[0]
    value = flavor[1]
    name = "Persistence.BTrees._%sBTree" % flavor
    sources = ["lib/python/Persistence/BTrees/_%sBTree.c" % flavor]
    kwargs = {"include_dirs": ["lib/python/Persistence"]}
    if flavor != "fs":
        kwargs["depends"] = (base_btrees_depends + [KEY_H % _flavors[key],
                                                    VALUE_H % _flavors[value]])
    if key != "O":
        kwargs["define_macros"] = [('EXCLUDE_INTSET_SUPPORT', None)]
    return Extension(name, sources, **kwargs)

ext_modules = [
    BTreeExtension("OO"), BTreeExtension("IO"), BTreeExtension("OI"),
    BTreeExtension("II"), BTreeExtension("fs"),
    Extension("Persistence.cPersistence",
              ["lib/python/Persistence/cPersistence.c"],
              depends = ["lib/python/Persistence/cPersistence.h",
                         "lib/python/Persistence/cPersistenceAPI.h",]),
    Extension("ZODB._TimeStamp", ["lib/python/ZODB/TimeStamp.c"]),
    Extension("ZODB.winlock", ["lib/python/ZODB/winlock.c"]),
    Extension("BDBStorage._helper", ["lib/python/BDBStorage/_helper.c"]),
    Extension("Zope.ContextWrapper.wrapper",
              ["lib/python/Zope/ContextWrapper/wrapper.c"],
              include_dirs = ["include"],
              depends = ["include/Zope/ContextWrapper/wrapper.h",
                         "include/Zope/Proxy/proxy.h"]),
    Extension("Zope.Proxy.proxy", ["lib/python/Zope/Proxy/proxy.c"],
              include_dirs = ["include"],
              depends = ["include/Zope/Proxy/proxy.h"]),
    Extension("Zope.Security._Proxy", ["lib/python/Zope/Security/_Proxy.c"],
              include_dirs = ["include"],
              depends = ["include/Zope/Proxy/proxy.h"]),
    ]

doclines = __doc__.split("\n")

setup(name="Zope3",
      version="3.0a1",
      maintainer="Zope Corporation",
      maintainer_email="zope3-dev@zope.org",
      ext_modules = ext_modules,
      headers = ["ZODB/cPersistence.h", "ZODB/cPersistenceAPI.h",
                 "Zope/Proxy/proxy.h", "Zope/ContextWrapper/wrapper.h"],
      license = "http://www.zope.org/Resources/ZPL",
      platforms = ["any"],
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      )
