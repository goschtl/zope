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

# provide a bunch of custom components that make it possible to install a non
# .py file into one of the packages
from distutils import dir_util
from distutils.command.build import build as buildcmd
from distutils.command.install_lib import install_lib as installcmd
from distutils.core import setup
from distutils.dist import Distribution
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


# We have to snoop for file types that distutils doesn't copy correctly when
# doing a non-build-in-place.
EXTS = ['.zcml', '.pt', '.gif', '.xml', '.html', '.png',
        '.css', '.js', '.conf', '.mo']


class Finder:
    def __init__(self, exts, prefix):
        self._files = []
        self._pkgs = {}
        self._exts = exts
        self._plen = len(prefix)

    def visit(self, ignore, dir, files):
        for file in files[:]:
            # First see if this is one of the packages we want to add, or if
            # we're really skipping this package.
            if '__init__.py' in files:
                aspkg = dir[self._plen:].replace(os.sep, '.')
                self._pkgs[aspkg] = True
            # Add any extra files we're interested in
            base, ext = os.path.splitext(file)
            if ext in self._exts:
                self._files.append(os.path.join(dir, file))

    def copy_files(self, cmd, outputbase):
        for file in self._files:
            dest = os.path.join(outputbase, file[self._plen:])
            # Make sure the destination directory exists
            dir = os.path.dirname(dest)
            if not os.path.exists(dir):
                dir_util.mkpath(dir)
            cmd.copy_file(file, dest)

    def get_packages(self):
        return self._pkgs.keys()


basedir = 'lib/python/'
finder = Finder(EXTS, basedir)
os.path.walk(basedir, finder.visit, None)
packages = finder.get_packages()

class MyBuilder(buildcmd):
    def run(self):
        buildcmd.run(self)
        finder.copy_files(self, self.build_lib)

class MyLibInstaller(installcmd):
    def run(self):
        installcmd.run(self)
        extra.copy_files(self, self.install_dir)


class MyDistribution(Distribution):
    # To control the selection of MyLibInstaller and MyPyBuilder, we
    # have to set it into the cmdclass instance variable, set in
    # Distribution.__init__().
    def __init__(self, *attrs):
        Distribution.__init__(self, *attrs)
        self.cmdclass['build'] = MyBuilder
        self.cmdclass['install_lib'] = MyLibInstaller


# The logging package is standard in Python 2.3.  Don't include it unless
# we're building a source distribution.
if 'sdist' not in sys.argv:
    if sys.hexversion >= 0x02030000:
        packages.remove('logging')


doclines = __doc__.split("\n")

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
    Extension("BDBStorage._helper", ["lib/python/BDBStorage/_helper.c"]),
    Extension("Zope.ContextWrapper.wrapper",
              ["lib/python/Zope/ContextWrapper/wrapper.c"],
              include_dirs = ["lib/python"],
              depends = ["lib/python/Zope/ContextWrapper/wrapper.h",
                         "lib/python/Zope/Proxy/proxy.h"]),
    Extension("Zope.Proxy.proxy", ["lib/python/Zope/Proxy/proxy.c"],
              include_dirs = ["lib/python"],
              depends = ["lib/python/Zope/Proxy/proxy.h"]),
    Extension("Zope.Security._Proxy", ["lib/python/Zope/Security/_Proxy.c"],
              include_dirs = ["lib/python"],
              depends = ["lib/python/Zope/Proxy/proxy.h"]),
    ]

if sys.platform == "win32":
    ext_modules += [Extension("ZODB.winlock", ["lib/python/ZODB/winlock.c"])]

doclines = __doc__.split("\n")

setup(name="Zope3",
      version="3.0a1",
      maintainer="Zope Corporation",
      maintainer_email="zope3-dev@zope.org",
      url = "http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture/FrontPage",
      ext_modules = ext_modules,
      # This doesn't work right at all
      headers = ["lib/python/Persistence/cPersistence.h",
                 "lib/python/Persistence/cPersistenceAPI.h",
                 "lib/python/Zope/Proxy/proxy.h",
                 "lib/python/Zope/ContextWrapper/wrapper.h"],
      license = "http://www.zope.org/Resources/ZPL",
      platforms = ["any"],
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      packages = packages,
      package_dir = {'': 'lib/python'},
      distclass = MyDistribution,
      )
