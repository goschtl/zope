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

"""Zope application server

Zope is a leading open source application server, specializing in content
management, portals, and custom applications.  Zope enables teams to
collaborate in the creation and management of dynamic web-based business
applications such as intranets and portals.
"""

classifiers = """\
Development Status :: 3 - Alpha
Environment :: Web Environment
License :: OSI Approved :: Zope Public License
Operating System :: Microsoft :: Windows
Operating System :: Unix
Programming Language :: Python
Topic :: Internet :: WWW/HTTP
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Software Development :: Libraries :: Python Modules
"""

import os
import sys

# Provide a bunch of custom components that make it possible to build and
# install non-.py files into the package destinations.
from distutils import dir_util
from distutils.command.build import build as buildcmd
from distutils.command.build_ext import build_ext
from distutils.command.install_lib import install_lib as installcmd
from distutils.core import setup
from distutils.dist import Distribution
from distutils.extension import Extension

if sys.version_info < (2, 3):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)


# A hack to determine if Extension objects support the `depends' keyword arg,
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
EXTS = ['.conf', '.css', '.dtd', '.gif', '.html',
        '.js',   '.mo',  '.png', '.pt', '.stx', '.ref',
        '.txt',  '.xml', '.zcml', '.mar',
        ]


# This class serves multiple purposes.  It walks the file system looking for
# auxiliary files that distutils doesn't install properly, and it actually
# copies those files (when hooked into by distutils).  It also walks the file
# system looking for candidate packages for distutils to install as normal.
# The key here is that the package must have an __init__.py file.
class Finder:
    def __init__(self, exts, prefix):
        self._files = []
        self._pkgs = {}
        self._exts = exts
        # We're finding packages in lib/python in the source dir, but we're
        # copying them directly under build/lib.<plat>.  So we need to lop off
        # the prefix when calculating the package names from the file names.
        self._plen = len(prefix)

    def visit(self, ignore, dir, files):
        for file in files:
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

def remove_stale_bytecode(arg, dirname, names):
    names = map(os.path.normcase, names)
    for name in names:
        if name.endswith(".pyc") or name.endswith(".pyo"):
            srcname = name[:-1]
            if srcname not in names:
                fullname = os.path.join(dirname, name)
                print "Removing stale bytecode file", fullname
                os.unlink(fullname)

# Create the finder instance, which will be used in lots of places.  `finder'
# is the global we're most interested in.
basedir = 'src/'
finder = Finder(EXTS, basedir)
os.path.walk(basedir, finder.visit, None)
packages = finder.get_packages()

# The logging package is standard in Python 2.3.  Don't include it unless
# we're building a source distribution.
if 'sdist' not in sys.argv:
    if sys.hexversion >= 0x02030000:
        packages.remove('logging')

# Distutils hook classes
class MyBuilder(buildcmd):
    def run(self):
        os.path.walk(os.curdir, remove_stale_bytecode, None)
        buildcmd.run(self)
        finder.copy_files(self, self.build_lib)

class MyExtBuilder(build_ext):
    # Override the default build_ext to remove stale bytecodes.
    # Technically, removing bytecode has nothing to do with
    # building extensions, but Zope's the build_ext -i variant
    # is used to build Zope in place.
    def run(self):
        os.path.walk(os.curdir, remove_stale_bytecode, None)
        build_ext.run(self)

class MyLibInstaller(installcmd):
    def run(self):
        installcmd.run(self)
        finder.copy_files(self, self.install_dir)

class MyDistribution(Distribution):
    # To control the selection of MyLibInstaller and MyPyBuilder, we
    # have to set it into the cmdclass instance variable, set in
    # Distribution.__init__().
    def __init__(self, *attrs):
        Distribution.__init__(self, *attrs)
        self.cmdclass['build'] = MyBuilder
        self.cmdclass['build_ext'] = MyExtBuilder
        self.cmdclass['install_lib'] = MyLibInstaller


# Set up dependencies for the BTrees package
base_btrees_depends = [
    "src/persistence/persistence.h",
    "src/persistence/persistenceAPI.h",
    "src/zodb/btrees/BTreeItemsTemplate.c",
    "src/zodb/btrees/BTreeModuleTemplate.c",
    "src/zodb/btrees/BTreeTemplate.c",
    "src/zodb/btrees/BucketTemplate.c",
    "src/zodb/btrees/MergeTemplate.c",
    "src/zodb/btrees/SetOpTemplate.c",
    "src/zodb/btrees/SetTemplate.c",
    "src/zodb/btrees/TreeSetTemplate.c",
    "src/zodb/btrees/sorters.c",
    ]

_flavors = {"O": "object", "I": "int"}

KEY_H = "src/zodb/btrees/%skeymacros.h"
VALUE_H = "src/zodb/btrees/%svaluemacros.h"

include_dirs = ['src']

def BTreeExtension(flavor):
    key = flavor[0]
    value = flavor[1]
    name = "zodb.btrees._zodb_btrees_%sBTree" % flavor
    sources = ["src/zodb/btrees/_zodb_btrees_%sBTree.c" % flavor]
    kwargs = {"include_dirs": include_dirs}
    if flavor != "fs":
        kwargs["depends"] = (base_btrees_depends + [KEY_H % _flavors[key],
                                                    VALUE_H % _flavors[value]])
    return Extension(name, sources, **kwargs)

# All Zope3 extension modules must be listed here.
ext_modules = [
    BTreeExtension("OO"),
    BTreeExtension("IO"),
    BTreeExtension("OI"),
    BTreeExtension("II"),
    BTreeExtension("fs"),
    Extension("persistence._persistence",
              ["src/persistence/persistence.c"],
              depends = ["src/persistence/persistence.h",
                         "src/persistence/persistenceAPI.h",]),
    Extension("zodb._timestamp", ["src/zodb/_timestamp.c"]),
    Extension("zodb.storage._helper", ["src/zodb/storage/_helper.c"]),
    Extension("zope.proxy.context.wrapper",
              ["src/zope/proxy/context/wrapper.c"],
              include_dirs = include_dirs,
              depends = ["src/zope/proxy/context/wrapper.h",
                         "src/zope/proxy/proxy.h"]),
    Extension("zope.proxy.context.decorator",
              ["src/zope/proxy/context/decorator.c"],
              include_dirs = include_dirs,
              depends = ["src/zope/proxy/context/decorator.h",
                         "src/zope/proxy/context/wrapper.h",
                         "src/zope/proxy/proxy.h"]),
    Extension("zope.proxy.proxy", ["src/zope/proxy/proxy.c"],
              include_dirs = include_dirs,
              depends = ["src/zope/proxy/proxy.h"]),
    Extension("zope.security._proxy", ["src/zope/security/_proxy.c"],
              include_dirs = include_dirs,
              depends = ["src/zope/proxy/proxy.h"]),

    
    Extension("zope.interface._zope_interface_ospec",
              ["src/zope/interface/_zope_interface_ospec.c"],
              include_dirs = include_dirs,
              depends = []),
    Extension("zope.hookable._zope_hookable",
              ["src/zope/hookable/_zope_hookable.c"],
              include_dirs = include_dirs,
              depends = []),
    ]

# On Window, there are more extensions that need to be built
if sys.platform == "win32":
    ext_modules += [Extension("zodb.winlock", ["src/zodb/winlock.c"])]


# We're using the module docstring as the distutils descriptions.
doclines = __doc__.split("\n")

setup(name="ZopeX3",
      version="3.0m2",
      maintainer="Zope Corporation",
      maintainer_email="zope3-dev@zope.org",
      url = "http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture",
      ext_modules = ext_modules,
      # This doesn't work right at all
      headers = ["src/persistence/persistence.h",
                 "src/persistence/persistenceAPI.h",
                 "src/zope/proxy/proxy.h",
                 "src/zope/proxy/context/wrapper.h"],
      license = "http://www.zope.org/Resources/ZPL",
      platforms = ["any"],
      description = doclines[0],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = "\n".join(doclines[2:]),
      packages = packages,
      package_dir = {'': 'src'},
      distclass = MyDistribution,
      )
