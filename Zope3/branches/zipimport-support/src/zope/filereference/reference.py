##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""References to package-relative resources.

"""
__docformat__ = "reStructuredText"

import __builtin__
import errno
import os
import StringIO
import zipimport

import zope.interface

from zope.filereference.interfaces import IResourceReference

try:
    import pkg_resources
except ImportError:
    pkg_resources = None


def exists(path):
    if IResourceReference.providedBy(path):
        return path.exists()
    else:
        return os.path.exists(path)


def isdir(path):
    if IResourceReference.providedBy(path):
        return path.isdir()
    else:
        return os.path.isdir(path)


def isfile(path):
    if IResourceReference.providedBy(path):
        return path.isfile()
    else:
        return os.path.isfile(path)


def open(path, mode="r"):
    if not mode.startswith("r"):
        raise ValueError("`mode` must be a read-only mode")
    if IResourceReference.providedBy(path):
        return path.open(mode)
    else:
        return __builtin__.open(path, mode)


def new(path, package=None, basepath=None):

    if os.path.isabs(path):
        return PathReference(path)

    # Got a relative path, combine with base path.
    # If we have no basepath, compute the base path from the package
    # path.

    if not basepath:
        if package is None:
            basepath = os.getcwd()
        else:
            basepath = os.path.dirname(package.__file__)

    p = os.path.join(basepath, path)
    p = os.path.normpath(p)
    p = os.path.abspath(p)

    if package:
        loader = getattr(package, "__loader__", None)
        if isinstance(loader, zipimport.zipimporter):
            return ZipImporterPackagePathReference(p, package, path)
        else:
            return PackagePathReference(p, package, path)
    else:
        return PathReference(p)


class PathReference(str):

    zope.interface.implements(IResourceReference)

    def __add__(self, other):
        path = str(self) + other
        return self.__class__(path)

    def open(self, mode="r"):
        return __builtin__.open(self, mode)

    def isfile(self):
        return os.path.isfile(self)

    def isdir(self):
        return os.path.isdir(self)

    def exists(self):
        return os.path.exists(self)


class PackageStr(str):

    zope.interface.implements(IResourceReference)

    def __add__(self, other):
        value = str(self) + other
        relpath = self._relpath + other
        return self.__class__(value, self._package, relpath)


class PackagePathReference(PackageStr):

    def __new__(cls, value, package, relpath):
        assert package
        self = str.__new__(cls, value)
        self._package = package
        self._relpath = relpath
        return self

    def open_pkg_resources(self, mode="r"):
        return _open_packaged_resource(
            self,
            mode,
            pkg_resources.resource_string,
            self._package.__name__,
            self._relpath)

    def open_path_or_loader(self, mode="r"):
        try:
            loader = self._package.__loader__
        except AttributeError:
            for dir in self._package.__path__:
                filename = os.path.join(dir, self._relpath)
                if os.path.exists(filename):
                    break
            return __builtin__.open(filename, mode)
        else:
            dir = os.path.dirname(self._package.__file__)
            filename = os.path.join(dir, self._relpath)
            return _open_packaged_resource(
                self, mode, loader.get_data, filename)

    def open(self, mode="r"):
        #
        # This separate wrapper method is used so that this can always
        # be tested for the case when pkg_resources is not available.
        # See tests.py for how the pkg_resources global is
        # manipulated.
        #
        if pkg_resources:
            return self.open_pkg_resources(mode)
        else:
            return self.open_path_or_loader(mode)

    def isfile(self):
        try:
            f = self.open()
        except IOError:
            return False
        f.close()
        return True

    def isdir(self):
        if pkg_resources:
            return pkg_resources.resource_isdir(
                self._package.__name__, self._relpath)
        else:
            try:
                loader = self._package.__loader__
            except AttributeError:
                for dir in self._package.__path__:
                    filename = os.path.join(dir, self._relpath)
                    if os.path.isdir(filename):
                        return True
                return False
            else:
                dir = os.path.dirname(self._package.__file__)
                path = os.path.join(dir, self._relpath)
                try:
                    if loader.is_package(path):
                        return True
                except zipimport.ZipImportError:
                    pass
                try:
                    loader.get_data(path)
                except IOError:
                    pass
                else:
                    return False

    def exists(self):
        if pkg_resources:
            return pkg_resources.resource_exists(
                self._package.__name__, self._relpath)
        else:
            try:
                loader = self._package.__loader__
            except AttributeError:
                for dir in self._package.__path__:
                    filename = os.path.join(dir, self._relpath)
                    if os.path.exists(filename):
                        return True
                return False
            else:
                dir = os.path.dirname(self._package.__file__)
                path = os.path.join(dir, self._relpath)
                try:
                    if loader.is_package(path):
                        return True
                except zipimport.ZipImportError:
                    pass
                try:
                    loader.get_data(path)
                except IOError:
                    pass
                else:
                    return True


class ZipImporterPackagePathReference(PackageStr):

    def __new__(cls, value, package, relpath):
        assert package
        assert isinstance(package.__loader__, zipimport.zipimporter)
        self = str.__new__(cls, value)
        self._package = package
        self._relpath = relpath
        self._loader = package.__loader__
        return self

    def open(self, mode="r"):
        dir = os.path.dirname(self._package.__file__)
        filename = os.path.join(dir, self._relpath)
        return _open_packaged_resource(
            self, mode, self._loader.get_data, filename)

    def exists(self):
        relpath = self._getpath()
        if relpath in self._loader._files:
            return True
        relpath += os.path.sep
        return relpath in self._loader._files

    def isdir(self):
        relpath = self._getpath()
        return (relpath + os.sep) in self._loader._files

    def isfile(self):
        relpath = self._getpath()
        return relpath in self._loader._files

    def _getpath(self):
        relpath = self._relpath.replace("/", os.sep)
        if os.altsep:
            relpath = relpath.replace(os.altsep, os.sep)
        while relpath.endswith(os.sep):
            relpath = relpath[:-len(os.sep)]
        pkglastname = self._package.__name__.split(".")[-1]
        relpath = os.path.join(self._loader.prefix, pkglastname, relpath)
        return relpath


def _open_packaged_resource(self, mode, opener, *args):
    try:
        data = opener(*args)
    except IOError, e:
        if len(e.args) == 1:
            raise IOError(errno.ENOENT, "file not found", self)
        else:
            raise
    if ("b" not in mode) and os.linesep != "\n":
        data = data.replace(os.linesep, "\n")
    f = StringIO.StringIO(data)
    f.name = self
    f.mode = mode
    return f
