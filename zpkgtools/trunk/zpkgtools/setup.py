##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Generator for distutils setup.py files."""

import errno
import logging
import os
import posixpath
import sys

from zpkgtools import include
from zpkgtools import package
from zpkgtools import publication


_logger = logging.getLogger(__name__)


class SetupContext:
    """Object representing the arguments to distutils.core.setup()."""

    def __init__(self, pkgname, version, setup_file):
        self._working_dir = os.path.dirname(os.path.abspath(setup_file))
        self.version = version
        self.packages = []
        self.package_data = {}
        self.package_dir = {}
        self.ext_modules = []
        self.scripts = []
        self.platforms = None
        self.classifiers = None
        self.load_metadata(
            os.path.join(self._working_dir, pkgname,
                         publication.PUBLICATION_CONF))
        pkgdir = os.path.join(self._working_dir, pkgname)
        self.scan(pkgname, pkgdir, pkgname)
        depsdir = os.path.join(self._working_dir, "Dependencies")
        if os.path.isdir(depsdir):
            depnames = os.listdir(depsdir)
            suffix = "-%s-%s" % (pkgname, version)
            for name in depnames:
                if name != "Includes" and not name.endswith(suffix):
                    # an unexpected name; we didn't put this here!
                    print >>sys.stderr, \
                          "unexpected name in Dependencies/: %r" % name
                    continue
                depdir = os.path.join(depsdir, name)
                if not os.path.isdir(depdir):
                    # a file; we didn't put this here either!
                    print >>sys.stderr, \
                          "unexpected file in Dependencies/: %r" % name
                    continue
                depname = name[:-len(suffix)]
                pkgdir = os.path.join(depdir, depname)
                reldir = posixpath.join("Dependencies", name, depname)
                self.scan(depname, pkgdir, reldir)
            includes_dir = os.path.join(depsdir, "Includes")
            if os.path.isdir(includes_dir):
                for ext in self.ext_modules:
                    ext.include_dirs.append(includes_dir)

    def setup(self):
        kwargs = self.__dict__.copy()
        for name in self.__dict__:
            if name[0] == "_":
                del kwargs[name]
        if "--debug" in sys.argv:
            import pprint
            try:
                pprint.pprint(kwargs)
            except IOError, e:
                if e.errno != errno.EPIPE:
                    raise
        else:
            root_logger = logging.getLogger()
            if not root_logger.handlers:
                root_logger.addHandler(logging.StreamHandler())
            try:
                from setuptools import setup
            except ImportError:
                # package_data can't be handled this way ;-(
                if self.package_data:
                    _logger.error(
                        "can't import setuptools;"
                        " some package data will not be properly installed")
                from distutils.core import setup
            setup(**kwargs)

    def load_metadata(self, path):
        f = open(path, "rU")
        publication.load(f, metadata=self)
        if self.platforms:
            self.platforms = ", ".join(self.platforms)

    def scan(self, name, directory, reldir):
        init_py = os.path.join(directory, "__init__.py")
        if os.path.isfile(init_py):
            self.scan_package(name, directory, reldir)
        else:
            self.scan_collection(name, directory, reldir)

    def scan_collection(self, name, directory, reldir):
        # load the collection metadata
        pkginfo = package.loadCollectionInfo(directory, reldir)
        self.scripts.extend(pkginfo.script)

    def scan_package(self, name, directory, reldir):
        # load the package metadata
        pkginfo = package.loadPackageInfo(name, directory, reldir)
        self.scripts.extend(pkginfo.script)
        self.ext_modules.extend(pkginfo.extensions)
        self.add_package_dir(name, reldir)

        # scan the files in the directory:
        files = include.filter_names(os.listdir(directory))
        for fn in files:
            fnbase, ext = os.path.splitext(fn)
            path = os.path.join(directory, fn)
            if os.path.isdir(path):
                init_py = os.path.join(path, "__init__.py")
                if os.path.isfile(init_py):
                    # if this package is published separately, skip it:
                    if os.path.isfile(
                        os.path.join(path, publication.PUBLICATION_CONF)):
                        continue
                    pkgname = "%s.%s" % (name, fn)
                    self.scan_package(
                        pkgname, path, posixpath.join(reldir, fn))
                else:
                    # an ordinary directory
                    self.scan_directory(name, path, fn)
            else:
                self.add_package_file(name, fn)

        # We need to check that any files that were labelled as
        # scripts aren't copied in as package data; they shouldn't be
        # installed into the package itself.
        #
        # XXX I'm not sure whether documentation files should be
        # removed from package_data or not, given that there's no spec
        # for installing documentation other than for RPMs.
        #
        relbase = posixpath.join(reldir, "")
        pkgfiles = self.package_data.get(reldir, [])
        for script in pkginfo.script:
            pkgdatapath = script[len(relbase):]
            if pkgdatapath in pkgfiles:
                pkgfiles.remove(pkgdatapath)

    def scan_directory(self, pkgname, directory, reldir):
        """Scan a data directory, adding files to package_data."""
        files = include.filter_names(os.listdir(directory))
        for fn in files:
            path = os.path.join(directory, fn)
            if os.path.isdir(path):
                self.scan_directory(pkgname,
                                    os.path.join(directory, fn),
                                    posixpath.join(reldir, fn))
            else:
                fnbase, ext = os.path.splitext(fn)
                if ext in (".pyc", ".pyo", ".so", ".sl", ".pyd"):
                    continue
                self.add_package_file(pkgname, posixpath.join(reldir, fn))

    def add_package_dir(self, pkgname, reldir):
        self.packages.append(pkgname)
        if pkgname.replace(".", posixpath.sep) != reldir:
            self.package_dir[pkgname] = reldir

    def add_package_file(self, pkgname, relfn):
        # Only add the file as package data if it's not a Python
        # source file; Python files are copied in automatically.
        if not relfn.endswith(".py"):
            L = self.package_data.setdefault(pkgname, [])
            L.append(relfn)
